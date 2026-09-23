from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models import RoleEnum, AuthProviderEnum

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: RoleEnum
    auth_provider: AuthProviderEnum
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

class UserRoleUpdate(BaseModel):
    role: RoleEnum
