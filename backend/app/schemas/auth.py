from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models import RoleEnum, AuthProviderEnum

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: RoleEnum
    auth_provider: AuthProviderEnum
    avatar_url: Optional[str] = None

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: Optional[RoleEnum] = RoleEnum.VIEWER
