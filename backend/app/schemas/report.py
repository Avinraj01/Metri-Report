from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models import ReportStatusEnum, TestStatusEnum

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_number: str
    session_id: str
    instrument_id: str
    version: str
    status: ReportStatusEnum
    overall_result: TestStatusEnum
    reviewer_comments: Optional[str] = None
    approver_comments: Optional[str] = None
    pdf_path: Optional[str] = None
    docx_path: Optional[str] = None
    generated_by_id: Optional[str] = None
    reviewed_by_id: Optional[str] = None
    approved_by_id: Optional[str] = None
    finalized_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ReportReviewAction(BaseModel):
    action: str  # "SUBMIT", "APPROVE", "REJECT", "FINALIZE", "REVISE"
    comments: Optional[str] = None
