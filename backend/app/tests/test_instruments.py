def test_create_instrument_success(client, engineer_headers):
    payload = {
        "instrument_name": "QA Bench Scale Model B100",
        "model": "B-100",
        "instrument_type": "Bench Weighing Scale",
        "serial_number": "SN-QA-B100-2026",
        "manufacturer": "Indian Metrology Instruments Ltd.",
        "manufacturer_address": "Bangalore, India",
        "applicant_name": "Indian Metrology Instruments Ltd.",
        "accuracy_class": "III",
        "max_capacity": 150.0,
        "min_capacity": 1.0,
        "e_value": 0.05,
        "d_value": 0.05,
        "unit": "kg",
        "num_support_points": 4,
        "temp_min": -10.0,
        "temp_max": 40.0
    }
    response = client.post("/api/instruments", json=payload, headers=engineer_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["model"] == "B-100"
    assert data["n_intervals"] == 3000  # 150 / 0.05

def test_instrument_validation_max_le_min(client, engineer_headers):
    payload = {
        "instrument_name": "Faulty Scale",
        "model": "F-10",
        "instrument_type": "Bench Scale",
        "serial_number": "SN-FAULT-001",
        "manufacturer": "Faulty Corp",
        "applicant_name": "Faulty Corp",
        "accuracy_class": "III",
        "max_capacity": 10.0,
        "min_capacity": 20.0,  # Invalid: Min > Max
        "e_value": 0.1,
        "d_value": 0.1,
        "unit": "kg"
    }
    response = client.post("/api/instruments", json=payload, headers=engineer_headers)
    assert response.status_code == 422
    assert "Max capacity must be strictly greater than Min capacity" in response.text

def test_instrument_validation_d_greater_than_e(client, engineer_headers):
    payload = {
        "instrument_name": "Invalid d Scale",
        "model": "D-FAIL",
        "instrument_type": "Bench Scale",
        "serial_number": "SN-DFAIL-002",
        "manufacturer": "Test Corp",
        "applicant_name": "Test Corp",
        "accuracy_class": "III",
        "max_capacity": 100.0,
        "min_capacity": 1.0,
        "e_value": 0.01,
        "d_value": 0.05,  # Invalid: d > e (OIML R 76-1 Cl. 3.1.2)
        "unit": "kg"
    }
    response = client.post("/api/instruments", json=payload, headers=engineer_headers)
    assert response.status_code == 422
    assert "cannot be greater than verification scale interval e" in response.text

def test_list_and_search_instruments(client, engineer_headers):
    response = client.get("/api/instruments?search=MW-3000", headers=engineer_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["model"] == "MW-3000"
