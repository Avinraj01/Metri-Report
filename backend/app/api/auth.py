from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token, verify_google_token
from app.models import User, RoleEnum, AuthProviderEnum
from app.schemas.auth import LoginRequest, GoogleLoginRequest, TokenResponse, UserRegisterRequest
from app.schemas.user import UserResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive or not found")
    return user

def get_optional_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None
    return user

def require_role(allowed_roles: list):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role {current_user.role.value}. Required: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

@router.post("/login", response_model=TokenResponse)
def login_local(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Standard Local / Offline Demo authentication with email & password.
    """
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role.value})
    AuditService.log_event(db, "USER_LOGIN_LOCAL", "User", user.id, user=user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        auth_provider=user.auth_provider,
        avatar_url=user.avatar_url
    )

@router.post("/google", response_model=TokenResponse)
def login_google(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Unified Google OAuth 2.0 / OpenID Connect authentication.
    Verifies Google ID token, performs secure account linking, enforces verified email,
    and assigns safe default role VIEWER without auto-escalation.
    """
    payload = verify_google_token(req.id_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired or unverified Google OAuth token"
        )

    google_sub = payload.get("sub")
    email = payload.get("email", "").lower().strip()
    name = payload.get("name", "Google User")
    picture = payload.get("picture")

    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email missing in Google token payload")

    # Look up existing user by google_id or verified email
    user = db.query(User).filter((User.google_id == google_sub) | (User.email == email)).first()

    if user:
        # Link Google ID if not already linked
        if not user.google_id:
            user.google_id = google_sub
            user.auth_provider = AuthProviderEnum.HYBRID if user.hashed_password else AuthProviderEnum.GOOGLE
        if picture and not user.avatar_url:
            user.avatar_url = picture
        db.commit()
    else:
        # Create new user with SAFE DEFAULT ROLE: VIEWER
        user = User(
            email=email,
            full_name=name,
            role=RoleEnum.VIEWER, # Strictly no auto-admin!
            auth_provider=AuthProviderEnum.GOOGLE,
            google_id=google_sub,
            avatar_url=picture,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role.value})
    AuditService.log_event(db, "USER_LOGIN_GOOGLE", "User", user.id, user=user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        auth_provider=user.auth_provider,
        avatar_url=user.avatar_url
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user details.
    """
    return current_user
