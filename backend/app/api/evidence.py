import os
import hashlib
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Evidence, User, RoleEnum
from app.schemas.evidence import EvidenceResponse
from app.api.auth import get_current_user, require_role
from app.services.audit_service import AuditService
from app.config import settings

router = APIRouter(prefix="/evidence", tags=["Evidence & Document Management"])

@router.get("", response_model=List[EvidenceResponse])
def list_all_evidence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all uploaded metrological evidence records.
    """
    return db.query(Evidence).order_by(Evidence.created_at.desc()).all()

@router.post("", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    instrument_id: Optional[str] = Form(None),
    test_code: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' not allowed. Permitted: {settings.ALLOWED_EXTENSIONS}"
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum permitted limit ({settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB)"
        )

    sha256_hash = hashlib.sha256(content).hexdigest()
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    evidence = Evidence(
        session_id=session_id,
        instrument_id=instrument_id,
        test_code=test_code,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        file_hash=sha256_hash,
        title=title,
        description=description,
        uploaded_by_id=current_user.id
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    AuditService.log_event(
        db, "EVIDENCE_UPLOADED", "Evidence", evidence.id,
        user=current_user, new_values={"filename": file.filename, "hash": sha256_hash, "title": title}
    )

    return evidence

@router.get("/session/{session_id}", response_model=List[EvidenceResponse])
def get_session_evidence(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Evidence).filter(Evidence.session_id == session_id).all()

@router.get("/instrument/{instrument_id}", response_model=List[EvidenceResponse])
def get_instrument_evidence(
    instrument_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Evidence).filter(Evidence.instrument_id == instrument_id).all()

@router.get("/{id}/download")
def download_evidence_file(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ev = db.query(Evidence).filter(Evidence.id == id).first()
    if not ev or not os.path.exists(ev.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence file not found")
    return FileResponse(ev.file_path, filename=ev.file_name, media_type=ev.file_type)
