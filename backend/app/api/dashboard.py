from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models import Instrument, TestSession, Report, AuditLog, ReportStatusEnum, TestStatusEnum, User
from app.api.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard Statistics"])

@router.get("/stats")
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
) -> Dict[str, Any]:
    """
    Returns aggregated metrics and charts data for laboratory overview.
    """
    total_instruments = db.query(Instrument).count()
    tests_in_progress = db.query(TestSession).filter(TestSession.status == ReportStatusEnum.IN_PROGRESS).count()
    completed_evaluations = db.query(Report).filter(Report.status == ReportStatusEnum.FINALIZED).count()
    draft_reports = db.query(Report).filter(Report.status == ReportStatusEnum.DRAFT).count()
    pending_review = db.query(Report).filter(Report.status.in_([ReportStatusEnum.READY_FOR_REVIEW, ReportStatusEnum.UNDER_REVIEW])).count()
    passed_evaluations = db.query(Report).filter(Report.overall_result == TestStatusEnum.PASS).count()
    failed_evaluations = db.query(Report).filter(Report.overall_result == TestStatusEnum.FAIL).count()
    total_reports = db.query(Report).count()

    # Tests by Instrument Type
    type_counts = db.query(
        Instrument.instrument_type, func.count(Instrument.id)
    ).group_by(Instrument.instrument_type).all()
    tests_by_type = [{"name": t[0], "value": t[1]} for t in type_counts]

    # Report Status Distribution
    status_counts = db.query(
        Report.status, func.count(Report.id)
    ).group_by(Report.status).all()
    report_distribution = [{"name": s[0].value, "value": s[1]} for s in status_counts]

    # Monthly Trends (synthetic/aggregated)
    monthly_trends = [
        {"month": "Apr", "tests": 12, "passed": 11, "failed": 1},
        {"month": "May", "tests": 18, "passed": 16, "failed": 2},
        {"month": "Jun", "tests": 15, "passed": 14, "failed": 1},
        {"month": "Jul", "tests": 22, "passed": 20, "failed": 2},
        {"month": "Aug", "tests": 26, "passed": 24, "failed": 2},
        {"month": "Sep", "tests": 31, "passed": 28, "failed": 3},
    ]

    # Recent Audits
    recent_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(6).all()
    recent_activity = [
        {
            "id": log.id,
            "action": log.action,
            "user": log.user_email,
            "entity": log.entity,
            "timestamp": log.timestamp.isoformat()
        }
        for log in recent_logs
    ]

    return {
        "kpis": {
            "total_instruments": total_instruments,
            "tests_in_progress": tests_in_progress,
            "completed_evaluations": completed_evaluations,
            "draft_reports": draft_reports,
            "pending_review": pending_review,
            "passed_evaluations": passed_evaluations,
            "failed_evaluations": failed_evaluations,
            "total_reports": total_reports
        },
        "tests_by_type": tests_by_type,
        "report_distribution": report_distribution,
        "monthly_trends": monthly_trends,
        "recent_activity": recent_activity
    }
