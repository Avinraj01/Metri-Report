from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User, RoleEnum, AuditLog
from app.schemas.user import UserResponse, UserRoleUpdate
from app.schemas.audit import AuditLogResponse
from app.api.auth import get_current_user, require_role
from app.services.audit_service import AuditService

users_router = APIRouter(prefix="/users", tags=["User & Role Management"])

@users_router.get("", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER]))
):
    return db.query(User).order_by(User.created_at.desc()).all()

@users_router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER]))
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_role = target_user.role.value
    target_user.role = data.role
    db.commit()
    db.refresh(target_user)

    AuditService.log_event(
        db, "USER_ROLE_CHANGED", "User", target_user.id,
        user=current_user, old_values={"role": old_role}, new_values={"role": target_user.role.value}
    )

    return target_user

audit_router = APIRouter(prefix="/audit-logs", tags=["Audit Trail"])

@audit_router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
