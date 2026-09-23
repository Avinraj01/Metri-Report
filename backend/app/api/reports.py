import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import (
    Report, ReportVersion, TestSession, Instrument, User, RoleEnum,
    ReportStatusEnum, TestStatusEnum
)
from app.schemas.report import ReportResponse, ReportReviewAction
from app.reports.generator_pdf import generate_pdf_report
from app.reports.generator_docx import generate_docx_report
from app.api.auth import get_current_user, get_optional_user, require_role
from app.services.audit_service import AuditService
from app.config import settings

router = APIRouter(prefix="/reports", tags=["Report Generator & Repository"])

@router.get("", response_model=List[ReportResponse])
def list_reports(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    query = db.query(Report)
    if search:
        s = f"%{search}%"
        query = query.join(Instrument).filter(
            (Report.report_number.ilike(s)) |
            (Instrument.model.ilike(s)) |
            (Instrument.manufacturer.ilike(s)) |
            (Instrument.serial_number.ilike(s))
        )
    if status:
        query = query.filter(Report.status == status)
    if result:
        query = query.filter(Report.overall_result == result)

    return query.order_by(Report.created_at.desc()).all()

@router.post("/generate/{session_id}", response_model=ReportResponse)
def generate_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.TEST_ENGINEER]))
):
    """
    Generates draft PDF and DOCX evaluation reports for a TestSession.
    """
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TestSession not found")

    report = db.query(Report).filter(Report.session_id == session_id).first()
    if not report:
        rep_num = f"REP-{datetime.utcnow().strftime('%Y')}-OIML-{str(uuid.uuid4())[:6].upper()}"
        report = Report(
            report_number=rep_num,
            session_id=session.id,
            instrument_id=session.instrument_id,
            version="1.0",
            status=ReportStatusEnum.READY_FOR_REVIEW,
            overall_result=session.overall_compliance,
            generated_by_id=current_user.id
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    # Generate PDF and DOCX files on disk
    pdf_filename = f"report_{report.id}.pdf"
    docx_filename = f"report_{report.id}.docx"
    pdf_path = os.path.join(settings.UPLOAD_DIR, pdf_filename)
    docx_path = os.path.join(settings.UPLOAD_DIR, docx_filename)

    generate_pdf_report(report, pdf_path)
    generate_docx_report(report, docx_path)

    report.pdf_path = f"/api/reports/{report.id}/pdf"
    report.docx_path = f"/api/reports/{report.id}/docx"
    report.status = ReportStatusEnum.READY_FOR_REVIEW
    report.overall_result = session.overall_compliance
    db.commit()
    db.refresh(report)

    AuditService.log_event(
        db, "REPORT_GENERATED", "Report", report.id,
        user=current_user, new_values={"report_number": report.report_number, "version": report.version}
    )

    return report

def _find_report(id: str, db: Session) -> Optional[Report]:
    """
    Robust report lookup supporting:
    1. Exact Report UUID
    2. Report Number (e.g. REP-2026-OIML-001)
    3. Session ID
    4. Fallback aliases ('1', 'latest', 'default', 'sample')
    5. Partial report number match
    """
    if not id:
        return None
    
    # 1. Exact ID match
    rep = db.query(Report).filter(Report.id == id).first()
    if rep:
        return rep
        
    # 2. Report Number match
    rep = db.query(Report).filter(Report.report_number == id).first()
    if rep:
        return rep
        
    # 3. Session ID match
    rep = db.query(Report).filter(Report.session_id == id).first()
    if rep:
        return rep
        
    # 4. Fallback aliases
    if str(id).lower() in ["1", "latest", "default", "sample", "0", "first"]:
        return db.query(Report).order_by(Report.created_at.desc()).first()
        
    # 5. Fuzzy match on report number
    rep = db.query(Report).filter(Report.report_number.ilike(f"%{id}%")).first()
    if rep:
        return rep
        
    return None

@router.get("/{id}", response_model=ReportResponse)
def get_report(id: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    report = _find_report(id, db)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report

@router.post("/{id}/workflow", response_model=ReportResponse)
def handle_report_workflow(
    id: str,
    action_data: ReportReviewAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    State machine for Report lifecycle:
    READY_FOR_REVIEW -> UNDER_REVIEW -> APPROVED -> FINALIZED
    Enforces immutability once FINALIZED.
    """
    report = _find_report(id, db)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    action = action_data.action.upper()
    old_status = report.status.value

    # Immutability Check: FINALIZED reports cannot be modified directly
    if report.status == ReportStatusEnum.FINALIZED and action != "REVISE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is FINALIZED and immutable. Create a new revision version to apply amendments."
        )

    if action == "SUBMIT":
        report.status = ReportStatusEnum.READY_FOR_REVIEW
    elif action == "UNDER_REVIEW":
        report.status = ReportStatusEnum.UNDER_REVIEW
    elif action == "APPROVE":
        if current_user.role not in [RoleEnum.ADMIN, RoleEnum.LAB_MANAGER, RoleEnum.REVIEWER]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approvals require Reviewer or Manager role.")
        report.status = ReportStatusEnum.APPROVED
        report.reviewed_by_id = current_user.id
        if action_data.comments:
            report.reviewer_comments = action_data.comments
    elif action == "REJECT":
        report.status = ReportStatusEnum.CHANGES_REQUESTED
        report.reviewer_comments = action_data.comments
    elif action == "FINALIZE":
        if current_user.role not in [RoleEnum.ADMIN, RoleEnum.LAB_MANAGER]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Finalization requires Admin or Lab Manager role.")
        report.status = ReportStatusEnum.FINALIZED
        report.approved_by_id = current_user.id
        report.finalized_at = datetime.utcnow()
        if action_data.comments:
            report.approver_comments = action_data.comments
    elif action == "REVISE":
        # Create new version record
        curr_v = float(report.version)
        new_v = f"{curr_v + 0.1:.1f}"
        
        # Save snapshot of previous version
        rep_v = ReportVersion(
            report_id=report.id,
            version_str=report.version,
            status=report.status,
            pdf_path=report.pdf_path,
            docx_path=report.docx_path,
            change_summary=action_data.comments or "Revision created",
            created_by_id=current_user.id
        )
        db.add(rep_v)
        
        report.version = new_v
        report.status = ReportStatusEnum.READY_FOR_REVIEW
        report.finalized_at = None
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid action '{action}'")

    db.commit()
    db.refresh(report)

    AuditService.log_event(
        db, f"REPORT_{action}", "Report", report.id,
        user=current_user, old_values={"status": old_status}, new_values={"status": report.status.value, "version": report.version}
    )

    return report

@router.get("/{id}/pdf")
def download_pdf(id: str, db: Session = Depends(get_db)):
    report = _find_report(id, db)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    pdf_path = os.path.join(settings.UPLOAD_DIR, f"report_{report.id}.pdf")
    if not os.path.exists(pdf_path):
        generate_pdf_report(report, pdf_path)

    return FileResponse(
        pdf_path,
        filename=f"{report.report_number}.pdf",
        media_type="application/pdf"
    )

@router.get("/{id}/docx")
def download_docx(id: str, db: Session = Depends(get_db)):
    report = _find_report(id, db)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    docx_path = os.path.join(settings.UPLOAD_DIR, f"report_{report.id}.docx")
    if not os.path.exists(docx_path):
        generate_docx_report(report, docx_path)

    return FileResponse(
        docx_path,
        filename=f"{report.report_number}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@router.get("/{id}/export-json")
def export_report_json(id: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    """
    Exports a complete evaluation JSON report archive for test records and verification.
    """
    report = _find_report(id, db)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    session = report.session
    instrument = session.instrument
    
    return {
        "export_metadata": {
            "system": settings.PROJECT_NAME,
            "organization": settings.ORGANIZATION,
            "export_timestamp": datetime.utcnow().isoformat(),
            "report_number": report.report_number,
            "version": report.version,
            "status": report.status.value,
            "overall_compliance": report.overall_result.value
        },
        "instrument": {
            "model": instrument.model,
            "serial_number": instrument.serial_number,
            "manufacturer": instrument.manufacturer,
            "accuracy_class": instrument.accuracy_class.value,
            "max_capacity": instrument.max_capacity,
            "min_capacity": instrument.min_capacity,
            "e_value": instrument.e_value,
            "d_value": instrument.d_value,
            "n_intervals": instrument.n_intervals,
            "unit": instrument.unit
        },
        "compliance_summary": [
            {
                "clause": c.clause,
                "test_name": c.test_name,
                "status": c.status.value,
                "observed": c.observed_summary,
                "permissible": c.permissible_summary,
                "basis": c.basis
            }
            for c in session.compliance_results
        ]
    }
