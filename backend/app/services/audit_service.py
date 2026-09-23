from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import AuditLog, User

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        action: str,
        entity: str,
        entity_id: str,
        user: Optional[User] = None,
        user_email: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Creates an immutable audit log entry.
        """
        email = user.email if user else (user_email or "system@metrireport.local")
        user_id = user.id if user else None

        audit = AuditLog(
            user_id=user_id,
            user_email=email,
            action=action,
            entity=entity,
            entity_id=str(entity_id),
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
