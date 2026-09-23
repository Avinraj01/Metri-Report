from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Standard, StandardVersion, StandardRule, User, RoleEnum
from app.schemas.rule import StandardRuleResponse
from app.api.auth import get_current_user, get_optional_user, require_role
from app.services.audit_service import AuditService

router = APIRouter(prefix="/standards", tags=["Standards & Versioned Rule Engine"])

@router.get("/rules", response_model=List[StandardRuleResponse])
def list_standard_rules(
    version: Optional[str] = "2006",
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    return db.query(StandardRule).filter(StandardRule.is_active == True).all()

@router.post("/rules/{rule_id}/toggle", response_model=StandardRuleResponse)
def toggle_rule_status(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER]))
):
    rule = db.query(StandardRule).filter(StandardRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)

    AuditService.log_event(
        db, "RULE_STATUS_TOGGLED", "StandardRule", rule.id,
        user=current_user, new_values={"rule_id": rule.rule_id, "is_active": rule.is_active}
    )

    return rule
