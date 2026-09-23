from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import CalculationResult, ComplianceResult, User, RoleEnum
from app.schemas.calculation import RunCalculationRequest, CalculationResultResponse, ComplianceResultResponse
from app.calculations.engine import CalculationEngine
from app.api.auth import get_current_user, require_role
from app.services.audit_service import AuditService

router = APIRouter(prefix="/calculations", tags=["Calculation & Compliance Engine"])

@router.post("/run")
def execute_session_calculations(
    req: RunCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    """
    Executes the verified Python calculation engine on all observations for a session.
    Computes Error E, Corrected Error Ec, MPE limits, repeatability, eccentricity, and creep.
    """
    try:
        res = CalculationEngine.run_session_calculations(db, req.session_id)
        AuditService.log_event(
            db, "CALCULATIONS_RUN", "TestSession", req.session_id,
            user=current_user, new_values=res
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Calculation engine error: {str(e)}")

@router.get("/session/{session_id}", response_model=List[CalculationResultResponse])
def get_session_calculations(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(CalculationResult).filter(CalculationResult.session_id == session_id).all()

@router.get("/compliance/{session_id}", response_model=List[ComplianceResultResponse])
def get_session_compliance_results(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns explainable compliance results (PASS/FAIL/MANUAL REVIEW) with exact OIML clauses.
    """
    return db.query(ComplianceResult).filter(ComplianceResult.session_id == session_id).all()
