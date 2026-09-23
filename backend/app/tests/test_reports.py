import os
from app.models import Report, TestSession, ReportStatusEnum, TestStatusEnum

def test_reports_list_and_filter(client, engineer_headers):
    response = client.get("/api/reports", headers=engineer_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(r["report_number"] == "REP-2026-OIML-001" for r in data)

def test_generate_report_endpoint(client, engineer_headers, db_session):
    session = db_session.query(TestSession).filter(TestSession.session_number == "TS-2026-001-MW3000").first()
    response = client.post(f"/api/reports/generate/{session.id}", headers=engineer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session.id
    assert "pdf_path" in data
    assert "docx_path" in data

def test_report_workflow_approval_and_immutability(client, admin_headers, reviewer_headers, engineer_headers, db_session):
    session = db_session.query(TestSession).filter(TestSession.session_number == "TS-2026-002-FAIL-DEMO").first()
    report = db_session.query(Report).filter(Report.session_id == session.id).first()

    # 1. Reviewer approves/reviews report
    resp_app = client.post(f"/api/reports/{report.id}/workflow", json={"action": "APPROVE", "comments": "Reviewed by Tech Reviewer"}, headers=reviewer_headers)
    assert resp_app.status_code == 200
    assert resp_app.json()["status"] == "APPROVED"

    # 2. Admin finalizes report
    resp_fin = client.post(f"/api/reports/{report.id}/workflow", json={"action": "FINALIZE", "comments": "Finalized by Lab Admin"}, headers=admin_headers)
    assert resp_fin.status_code == 200
    assert resp_fin.json()["status"] == "FINALIZED"

    # 3. Test Immutability: Attempting to edit/approve a FINALIZED report fails
    resp_blocked = client.post(f"/api/reports/{report.id}/workflow", json={"action": "APPROVE"}, headers=reviewer_headers)
    assert resp_blocked.status_code == 400
    assert "immutable" in resp_blocked.json()["detail"].lower()

    # 4. Test Versioning: Revise creates v1.1
    resp_rev = client.post(f"/api/reports/{report.id}/workflow", json={"action": "REVISE", "comments": "Amendment requested"}, headers=admin_headers)
    assert resp_rev.status_code == 200
    assert resp_rev.json()["version"] == "1.1"

def test_download_pdf_and_docx(client, db_session):
    report = db_session.query(Report).first()
    # PDF download
    resp_pdf = client.get(f"/api/reports/{report.id}/pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"

    # DOCX download
    resp_docx = client.get(f"/api/reports/{report.id}/docx")
    assert resp_docx.status_code == 200
    assert "wordprocessingml" in resp_docx.headers["content-type"]

def test_export_report_json(client, engineer_headers, db_session):
    report = db_session.query(Report).first()
    resp_json = client.get(f"/api/reports/{report.id}/export-json", headers=engineer_headers)
    assert resp_json.status_code == 200
    data = resp_json.json()
    assert "export_metadata" in data
    assert "compliance_summary" in data

def test_audit_logs_endpoint(client, engineer_headers):
    response = client.get("/api/audit-logs", headers=engineer_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
