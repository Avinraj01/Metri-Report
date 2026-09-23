import pytest
import os
import json
import hashlib
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token(email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]

def test_complete_laboratory_workflow_end_to_end():
    """
    SIH 2026 Comprehensive End-to-End Laboratory Evaluation Workflow
    1. Authenticate as TEST_ENGINEER
    2. Register NAWI Instrument (MW-3000)
    3. Initialize Test Session & Ambient Conditions
    4. Query Dynamic Applicable Tests Matrix
    5. Record Metrological Observations (Zero, Weighing, Eccentricity, Repeatability)
    6. Execute OIML R-76 Calculation & Compliance Engine
    7. Verify Explainable Compliance Results & MPE Margins
    8. Upload Evidence & Verify SHA-256 Cryptographic Hash
    9. Progress Review Workflow (DRAFT -> READY_FOR_REVIEW -> APPROVED -> FINALIZED)
    10. Generate & Verify Official PDF & DOCX Reports
    11. Verify Report Immutability (Modifications after finalization must be blocked)
    12. Verify Statutory Audit Trail Record Creation
    13. Verify RBAC Security (VIEWER / TEST_ENGINEER role boundaries)
    """
    
    # 1. Authenticate as Engineer
    engineer_token = get_auth_token("engineer@metrireport.local", "engineer123")
    engineer_headers = {"Authorization": f"Bearer {engineer_token}"}
    
    # 2. Register NAWI Instrument (MW-3000)
    inst_serial = f"SN-E2E-TEST-{os.urandom(4).hex().upper()}"
    inst_payload = {
        "instrument_name": "MW-3000 Electronic Platform Scale",
        "model": "MW-3000",
        "instrument_type": "Electronic Platform Scale",
        "serial_number": inst_serial,
        "manufacturer": "WeighTech Metrology India Ltd.",
        "manufacturer_address": "Plot 42, Electronics City, Bangalore, India",
        "applicant_name": "WeighTech Metrology India Ltd.",
        "applicant_address": "Plot 42, Electronics City, Bangalore, India",
        "accuracy_class": "III",
        "max_capacity": 3000.0,
        "min_capacity": 20.0,
        "e_value": 1.0,
        "d_value": 1.0,
        "unit": "kg",
        "load_receptor_type": "Platform",
        "num_support_points": 4,
        "load_cell_details": "4x Shear Beam Load Cells (OIML R60)",
        "indicator_details": "Digital LED Indicator Terminal",
        "software_version": "v1.0.0",
        "firmware_id": "FW-REV-100",
        "power_supply": "230 V AC, 50 Hz",
        "temp_min": -10.0,
        "temp_max": 40.0,
        "humidity_min": 20.0,
        "humidity_max": 85.0,
        "country_of_manufacture": "India",
        "application_use": "Commercial Trade & Legal Metrology Verification"
    }
    inst_res = client.post("/api/instruments", json=inst_payload, headers=engineer_headers)
    assert inst_res.status_code == 201
    instrument = inst_res.json()
    inst_id = instrument["id"]
    assert instrument["serial_number"] == inst_serial
    assert instrument["n_intervals"] == 3000

    # 3. Initialize Test Session & Ambient Conditions
    session_payload = {
        "instrument_id": inst_id,
        "session_name": f"E2E Evaluation Session - {inst_serial}",
        "ambient_temp": 22.5,
        "ambient_humidity": 55.0,
        "ambient_pressure": 1013.25,
        "ambient_voltage": 230.0,
        "notes": "E2E verification run in reference metrology lab."
    }
    sess_res = client.post("/api/test-sessions", json=session_payload, headers=engineer_headers)
    assert sess_res.status_code == 201
    session = sess_res.json()
    session_id = session["id"]
    assert session["status"] == "DRAFT"

    # 4. Query Dynamic Applicable Tests Matrix
    cat_res = client.get(f"/api/tests/applicable/{inst_id}", headers=engineer_headers)
    assert cat_res.status_code == 200
    applicable_tests = cat_res.json()
    assert len(applicable_tests) > 0
    test_codes = [t["test_code"] for t in applicable_tests]
    assert "A.4.2.3" in test_codes
    assert "A.4.4.1" in test_codes
    assert "A.4.7" in test_codes
    assert "A.4.10" in test_codes

    # 5. Record Metrological Observations (Zero, Weighing Points, Eccentricity, Repeatability)
    e_val = 1.0
    observations_data = [
        # A.4.2.3 Accuracy of Zero-Setting
        {"test_code": "A.4.2.3", "point_name": "Zero Point", "test_load": 0.0, "observed_indication": 0.0, "delta_load": 0.45 * e_val, "remarks": "Zero-setting verification"},
        # A.4.4.1 Weighing Performance (5 key steps across MPE tiers)
        {"test_code": "A.4.4.1", "point_name": "Min (20 kg)", "test_load": 20.0, "observed_indication": 20.0, "delta_load": 0.48 * e_val, "remarks": "Min capacity"},
        {"test_code": "A.4.4.1", "point_name": "500e (500 kg)", "test_load": 500.0, "observed_indication": 500.0, "delta_load": 0.42 * e_val, "remarks": "Tier 1 boundary"},
        {"test_code": "A.4.4.1", "point_name": "1/2 Max (1500 kg)", "test_load": 1500.0, "observed_indication": 1500.0, "delta_load": 0.35 * e_val, "remarks": "Mid range"},
        {"test_code": "A.4.4.1", "point_name": "2000e (2000 kg)", "test_load": 2000.0, "observed_indication": 2000.0, "delta_load": 0.30 * e_val, "remarks": "Tier 2 boundary"},
        {"test_code": "A.4.4.1", "point_name": "Max (3000 kg)", "test_load": 3000.0, "observed_indication": 3000.0, "delta_load": 0.25 * e_val, "remarks": "Max capacity"},
        # A.4.7 Eccentricity (1/3 Max = 1000 kg on 5 positions)
        {"test_code": "A.4.7", "point_name": "Center", "test_load": 1000.0, "observed_indication": 1000.0, "delta_load": 0.45 * e_val, "remarks": "Center position"},
        {"test_code": "A.4.7", "point_name": "Front-Left", "test_load": 1000.0, "observed_indication": 1000.0, "delta_load": 0.40 * e_val, "remarks": "Corner 1"},
        {"test_code": "A.4.7", "point_name": "Front-Right", "test_load": 1000.0, "observed_indication": 1000.0, "delta_load": 0.38 * e_val, "remarks": "Corner 2"},
        {"test_code": "A.4.7", "point_name": "Rear-Left", "test_load": 1000.0, "observed_indication": 1000.0, "delta_load": 0.42 * e_val, "remarks": "Corner 3"},
        {"test_code": "A.4.7", "point_name": "Rear-Right", "test_load": 1000.0, "observed_indication": 1000.0, "delta_load": 0.36 * e_val, "remarks": "Corner 4"},
        # A.4.10 Repeatability (3 runs at 1/2 Max = 1500 kg)
        {"test_code": "A.4.10", "point_name": "Run 1", "test_load": 1500.0, "observed_indication": 1500.0, "delta_load": 0.40 * e_val, "remarks": "Series 1"},
        {"test_code": "A.4.10", "point_name": "Run 2", "test_load": 1500.0, "observed_indication": 1500.0, "delta_load": 0.42 * e_val, "remarks": "Series 2"},
        {"test_code": "A.4.10", "point_name": "Run 3", "test_load": 1500.0, "observed_indication": 1500.0, "delta_load": 0.39 * e_val, "remarks": "Series 3"},
    ]
    batch_res = client.post(
        f"/api/test-sessions/{session_id}/batch-observations",
        json=observations_data,
        headers=engineer_headers
    )
    assert batch_res.status_code == 200

    # 6. Execute Calculation Engine
    calc_res = client.post("/api/calculations/run", json={"session_id": session_id}, headers=engineer_headers)
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["calculations_count"] > 0
    # Because only 4 of the applicable catalog tests are executed, overall compliance evaluates to MANUAL_REVIEW
    assert calc_data["overall_compliance"] == "MANUAL_REVIEW"

    # 7. Verify Compliance Results & MPE Margins
    comp_res = client.get(f"/api/calculations/compliance/{session_id}", headers=engineer_headers)
    assert comp_res.status_code == 200
    compliance_list = comp_res.json()
    assert len(compliance_list) >= 4
    for c in compliance_list:
        assert c["status"] == "PASS"
        assert c["basis"] is not None
        assert "OIML R 76-1:2006" in c["standard_reference"]

    # 8. Upload Evidence & Verify SHA-256 Cryptographic Hash
    sample_content = b"E2E METROLOGY CALIBRATION TEST CERTIFICATE & NAMEPLATE EVIDENCE"
    expected_sha256 = hashlib.sha256(sample_content).hexdigest()
    
    files = {"file": ("nameplate_test.png", sample_content, "image/png")}
    data = {"title": "MW-3000 Nameplate Evidence", "session_id": session_id, "instrument_id": inst_id}
    ev_res = client.post("/api/evidence", data=data, files=files, headers=engineer_headers)
    assert ev_res.status_code == 201
    ev_data = ev_res.json()
    assert ev_data["file_hash"] == expected_sha256
    assert ev_data["title"] == "MW-3000 Nameplate Evidence"

    # 9. Generate Report (READY_FOR_REVIEW)
    rep_res = client.post(f"/api/reports/generate/{session_id}", headers=engineer_headers)
    assert rep_res.status_code == 200
    report = rep_res.json()
    report_id = report["id"]
    assert report["overall_result"] == "MANUAL_REVIEW"
    assert report["status"] == "READY_FOR_REVIEW"

    # Reviewer reviews: READY_FOR_REVIEW -> APPROVED
    reviewer_token = get_auth_token("reviewer@metrireport.local", "reviewer123")
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}
    wf_res2 = client.post(
        f"/api/reports/{report_id}/workflow",
        json={"action": "APPROVE", "comments": "All OIML calculations verified against R-76 clauses."},
        headers=reviewer_headers
    )
    assert wf_res2.status_code == 200
    assert wf_res2.json()["status"] == "APPROVED"

    # Manager / Admin finalizes: APPROVED -> FINALIZED
    manager_token = get_auth_token("manager@metrireport.local", "manager123")
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    wf_res3 = client.post(
        f"/api/reports/{report_id}/workflow",
        json={"action": "FINALIZE", "comments": "Statutory seal applied."},
        headers=manager_headers
    )
    assert wf_res3.status_code == 200
    finalized_report = wf_res3.json()
    assert finalized_report["status"] == "FINALIZED"
    assert finalized_report["finalized_at"] is not None

    # 10. Generate & Verify Official PDF, DOCX, and JSON Exports
    pdf_res = client.get(f"/api/reports/{report_id}/pdf", headers=engineer_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    docx_res = client.get(f"/api/reports/{report_id}/docx", headers=engineer_headers)
    assert docx_res.status_code == 200
    assert "wordprocessingml.document" in docx_res.headers["content-type"]
    assert len(docx_res.content) > 1000

    json_export = client.get(f"/api/reports/{report_id}/export-json", headers=engineer_headers)
    assert json_export.status_code == 200
    export_data = json_export.json()
    assert export_data["export_metadata"]["report_number"] == finalized_report["report_number"]
    assert export_data["export_metadata"]["overall_compliance"] == "MANUAL_REVIEW"

    # 11. Verify Immutability Lock: Cannot modify finalized report
    attempt_modify = client.post(
        f"/api/reports/{report_id}/workflow",
        json={"action": "APPROVE", "comments": "Attempting illegal state edit."},
        headers=reviewer_headers
    )
    assert attempt_modify.status_code == 400

    # 12. Verify Statutory Audit Trail Record Creation
    admin_token = get_auth_token("admin@metrireport.local", "admin123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    audit_res = client.get("/api/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    audit_logs = audit_res.json()
    assert len(audit_logs) > 0
    actions = [l["action"] for l in audit_logs]
    assert "REGISTER_INSTRUMENT" in actions or "TEST_SESSION_CREATED" in actions or "CALCULATIONS_RUN" in actions

    # 13. Verify RBAC Security (Viewer cannot register instrument)
    viewer_token = get_auth_token("viewer@metrireport.local", "viewer123")
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
    viewer_inst_res = client.post("/api/instruments", json=inst_payload, headers=viewer_headers)
    assert viewer_inst_res.status_code == 403

def test_negative_failure_and_validation_scenarios():
    """
    Verifies that invalid loads, failing tolerances, and forbidden RBAC actions fail gracefully.
    """
    engineer_token = get_auth_token("engineer@metrireport.local", "engineer123")
    engineer_headers = {"Authorization": f"Bearer {engineer_token}"}

    # 1. Invalid instrument: Max capacity <= Min capacity
    bad_inst = {
        "instrument_name": "Invalid Balance",
        "model": "INV-100",
        "instrument_type": "Electronic Platform Scale",
        "serial_number": f"SN-INV-{os.urandom(4).hex()}",
        "manufacturer": "Bad Scales Corp",
        "applicant_name": "Bad Scales Corp",
        "accuracy_class": "III",
        "max_capacity": 10.0,
        "min_capacity": 50.0, # INVALID: Min > Max
        "e_value": 1.0,
        "d_value": 1.0,
        "unit": "kg"
    }
    res = client.post("/api/instruments", json=bad_inst, headers=engineer_headers)
    assert res.status_code in [400, 422]

    # 2. Failing test observation: Error exceeding MPE
    inst_res = client.post("/api/instruments", json={
        "instrument_name": "Test Failing Scale",
        "model": "FAIL-SCALE-100",
        "instrument_type": "Electronic Platform Scale",
        "serial_number": f"SN-FAIL-{os.urandom(4).hex()}",
        "manufacturer": "Fail Scale Co",
        "applicant_name": "Fail Scale Co",
        "accuracy_class": "III",
        "max_capacity": 1000.0,
        "min_capacity": 20.0,
        "e_value": 1.0,
        "d_value": 1.0,
        "unit": "kg"
    }, headers=engineer_headers)
    assert inst_res.status_code == 201
    f_inst_id = inst_res.json()["id"]

    sess_res = client.post("/api/test-sessions", json={
        "instrument_id": f_inst_id,
        "session_name": "Failing Test Session",
        "ambient_temp": 20.0,
        "ambient_humidity": 50.0,
        "ambient_pressure": 1013.25,
        "ambient_voltage": 230.0
    }, headers=engineer_headers)
    assert sess_res.status_code == 201
    f_sess_id = sess_res.json()["id"]

    # Record observation with huge error (Indication 510 kg for 500 kg load -> Error = +10 kg, MPE is 1.0 kg)
    client.post(f"/api/test-sessions/{f_sess_id}/batch-observations", json=[
        {"test_code": "A.4.4.1", "point_name": "500 kg", "test_load": 500.0, "observed_indication": 510.0, "delta_load": 0.5, "remarks": "Failing point"}
    ], headers=engineer_headers)

    client.post("/api/calculations/run", json={"session_id": f_sess_id}, headers=engineer_headers)
    comp_res = client.get(f"/api/calculations/compliance/{f_sess_id}", headers=engineer_headers)
    assert comp_res.status_code == 200
    comp_list = comp_res.json()
    assert any(c["status"] == "FAIL" for c in comp_list)

    # Generated report must reflect FAIL overall result
    rep_res = client.post(f"/api/reports/generate/{f_sess_id}", headers=engineer_headers)
    assert rep_res.status_code == 200
    assert rep_res.json()["overall_result"] == "FAIL"
