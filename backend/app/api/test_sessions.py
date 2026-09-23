import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import (
    TestSession, Instrument, TestObservation, User, RoleEnum, ReportStatusEnum, TestStatusEnum
)
from app.schemas.test_session import (
    TestSessionCreate, TestSessionUpdateConditions, TestSessionResponse,
    ObservationInput, ObservationResponse
)
from app.api.auth import get_current_user, require_role
from app.services.audit_service import AuditService

router = APIRouter(prefix="/test-sessions", tags=["Test Sessions & Observations"])

@router.get("", response_model=List[TestSessionResponse])
def list_test_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(TestSession).order_by(TestSession.created_at.desc()).all()

@router.post("", response_model=TestSessionResponse, status_code=status.HTTP_201_CREATED)
def create_test_session(
    data: TestSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    inst = db.query(Instrument).filter(Instrument.id == data.instrument_id).first()
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instrument not found")

    session_num = f"TS-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    session = TestSession(
        session_number=session_num,
        instrument_id=inst.id,
        session_name=data.session_name,
        ambient_temp=data.ambient_temp,
        ambient_humidity=data.ambient_humidity,
        ambient_pressure=data.ambient_pressure,
        ambient_voltage=data.ambient_voltage,
        test_engineer_id=current_user.id,
        notes=data.notes,
        status=ReportStatusEnum.DRAFT,
        overall_compliance=TestStatusEnum.NOT_TESTED
    )
    db.add(session)
    inst.status = "IN_TESTING"
    db.commit()
    db.refresh(session)

    AuditService.log_event(
        db, "TEST_SESSION_CREATED", "TestSession", session.id,
        user=current_user, new_values={"session_number": session.session_number, "instrument_id": inst.id}
    )

    return session

@router.get("/{id}", response_model=TestSessionResponse)
def get_test_session(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(TestSession).filter(TestSession.id == id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TestSession not found")
    return session

@router.put("/{id}/conditions", response_model=TestSessionResponse)
def update_ambient_conditions(
    id: str,
    data: TestSessionUpdateConditions,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    session = db.query(TestSession).filter(TestSession.id == id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TestSession not found")

    session.ambient_temp = data.ambient_temp
    session.ambient_humidity = data.ambient_humidity
    session.ambient_pressure = data.ambient_pressure
    session.ambient_voltage = data.ambient_voltage
    if data.notes:
        session.notes = data.notes

    db.commit()
    db.refresh(session)
    return session

@router.get("/{id}/observations", response_model=List[ObservationResponse])
def get_session_observations(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(TestObservation).filter(TestObservation.session_id == id).all()

@router.post("/{id}/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
def record_observation(
    id: str,
    data: ObservationInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    session = db.query(TestSession).filter(TestSession.id == id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TestSession not found")

    obs = TestObservation(
        session_id=session.id,
        test_code=data.test_code,
        point_name=data.point_name,
        test_load=data.test_load,
        observed_indication=data.observed_indication,
        delta_load=data.delta_load,
        remarks=data.remarks,
        raw_data=data.raw_data or {},
        status=TestStatusEnum.NOT_TESTED
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs

@router.post("/{id}/batch-observations", response_model=List[ObservationResponse])
def record_batch_observations(
    id: str,
    observations: List[ObservationInput],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    session = db.query(TestSession).filter(TestSession.id == id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TestSession not found")

    created = []
    for data in observations:
        obs = TestObservation(
            session_id=session.id,
            test_code=data.test_code,
            point_name=data.point_name,
            test_load=data.test_load,
            observed_indication=data.observed_indication,
            delta_load=data.delta_load,
            remarks=data.remarks,
            raw_data=data.raw_data or {},
            status=TestStatusEnum.NOT_TESTED
        )
        db.add(obs)
        created.append(obs)
    
    db.commit()
    for o in created:
        db.refresh(o)
    return created
