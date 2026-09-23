from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Instrument, User, RoleEnum
from app.schemas.instrument import InstrumentCreate, InstrumentUpdate, InstrumentResponse
from app.api.auth import get_current_user, get_optional_user, require_role
from app.services.audit_service import AuditService

router = APIRouter(prefix="/instruments", tags=["Instrument Registry"])

@router.get("", response_model=List[InstrumentResponse])
def list_instruments(
    search: Optional[str] = Query(None, description="Search by model, name, manufacturer, serial"),
    accuracy_class: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    List registered NAWI instruments with optional search and filters.
    """
    query = db.query(Instrument)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Instrument.model.ilike(s)) |
            (Instrument.instrument_name.ilike(s)) |
            (Instrument.manufacturer.ilike(s)) |
            (Instrument.serial_number.ilike(s))
        )
    if accuracy_class:
        query = query.filter(Instrument.accuracy_class == accuracy_class)
    if status:
        query = query.filter(Instrument.status == status)

    return query.order_by(Instrument.created_at.desc()).all()

@router.post("", response_model=InstrumentResponse, status_code=status.HTTP_201_CREATED)
def register_instrument(
    data: InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    """
    Registers a new weighing instrument after strict physical & metrological validation.
    """
    # Check duplicate serial number
    existing = db.query(Instrument).filter(Instrument.serial_number == data.serial_number.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An instrument with serial number '{data.serial_number}' is already registered."
        )

    # Compute n_intervals = Max / e
    n_calc = int(round(data.max_capacity / data.e_value))
    inst_dict = data.model_dump()
    inst_dict["n_intervals"] = n_calc
    inst_dict["status"] = "REGISTERED"

    instrument = Instrument(**inst_dict)
    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    AuditService.log_event(
        db, "INSTRUMENT_REGISTERED", "Instrument", instrument.id,
        user=current_user, new_values={"model": instrument.model, "serial": instrument.serial_number}
    )

    return instrument

@router.get("/{id}", response_model=InstrumentResponse)
def get_instrument_by_id(id: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    inst = db.query(Instrument).filter(Instrument.id == id).first()
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instrument not found")
    return inst

@router.put("/{id}", response_model=InstrumentResponse)
def update_instrument(
    id: str,
    data: InstrumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    inst = db.query(Instrument).filter(Instrument.id == id).first()
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instrument not found")

    old_vals = {"model": inst.model, "max_capacity": inst.max_capacity, "status": inst.status}
    update_data = data.model_dump(exclude_unset=True)

    for k, v in update_data.items():
        setattr(inst, k, v)

    # Recalculate n if max or e changed
    if "max_capacity" in update_data or "e_value" in update_data:
        inst.n_intervals = int(round(inst.max_capacity / inst.e_value))

    db.commit()
    db.refresh(inst)

    AuditService.log_event(
        db, "INSTRUMENT_UPDATED", "Instrument", inst.id,
        user=current_user, old_values=old_vals, new_values=update_data
    )

    return inst
