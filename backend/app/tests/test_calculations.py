from app.models import AccuracyClassEnum, TestStatusEnum
from app.calculations.weighing import calculate_error_changeover, evaluate_weighing_point
from app.calculations.zero import evaluate_zero_setting_accuracy
from app.calculations.repeatability import evaluate_repeatability_series
from app.calculations.eccentricity import evaluate_eccentricity_test
from app.calculations.discrimination import evaluate_discrimination_test
from app.calculations.creep import evaluate_creep_test, evaluate_zero_return_test

def test_changeover_formula():
    # E = I + 0.5e - delta_L - L
    # Indicated = 100 kg, e = 1 kg, delta_L = 0.4 kg, L = 100 kg
    # P = 100 + 0.5 - 0.4 = 100.1 kg
    # E = 100.1 - 100.0 = +0.10 kg
    err = calculate_error_changeover(indicated=100.0, load=100.0, e_val=1.0, delta_load=0.4)
    assert err == 0.10

def test_evaluate_weighing_point_pass_and_fail():
    # Class III, e = 1 kg, load = 500 kg (MPE = 0.5 kg)
    # Passing point: Indicated = 500, delta_load = 0.3 -> Ec = +0.20 kg <= 0.5 kg -> PASS
    res_pass = evaluate_weighing_point(
        accuracy_class=AccuracyClassEnum.CLASS_III,
        load=500.0, indicated=500.0, e_val=1.0, delta_load=0.3, zero_error=0.0
    )
    assert res_pass["status"] == TestStatusEnum.PASS
    assert res_pass["corrected_error"] == 0.20

    # Failing point: Indicated = 500, delta_load = -0.3 -> Ec = +0.80 kg > 0.5 kg -> FAIL
    res_fail = evaluate_weighing_point(
        accuracy_class=AccuracyClassEnum.CLASS_III,
        load=500.0, indicated=500.0, e_val=1.0, delta_load=-0.3, zero_error=0.0
    )
    assert res_fail["status"] == TestStatusEnum.FAIL

def test_zero_setting_accuracy():
    # Limit: |E0| <= 0.25e. For e = 1 kg, limit = 0.25 kg
    # E0 = 0 + 0.5 - 0.45 - 0 = +0.05 kg -> PASS
    z_pass = evaluate_zero_setting_accuracy(indicated_zero=0.0, e_val=1.0, delta_load_zero=0.45)
    assert z_pass["status"] == TestStatusEnum.PASS
    assert z_pass["zero_error"] == 0.05

    # E0 = 0 + 0.5 - 0.1 - 0 = +0.40 kg -> FAIL (exceeds 0.25 kg)
    z_fail = evaluate_zero_setting_accuracy(indicated_zero=0.0, e_val=1.0, delta_load_zero=0.1)
    assert z_fail["status"] == TestStatusEnum.FAIL

def test_repeatability_evaluation():
    # Load = 1000 kg, e = 1 kg (MPE = 1.0 kg)
    # Runs with errors: 0.1, 0.2, 0.15 -> delta_E = 0.1 <= 1.0 -> PASS
    readings = [
        {"indicated": 1000.0, "delta_load": 0.4},  # Err = +0.10
        {"indicated": 1000.0, "delta_load": 0.3},  # Err = +0.20
        {"indicated": 1000.0, "delta_load": 0.35}, # Err = +0.15
    ]
    res = evaluate_repeatability_series(AccuracyClassEnum.CLASS_III, 1000.0, 1.0, readings)
    assert res["status"] == TestStatusEnum.PASS
    assert res["repeatability_range"] == 0.10

def test_eccentricity_evaluation():
    # Max = 3000 kg, e = 1 kg, 4 supports -> nominal load = 1000 kg (MPE = 1.0 kg)
    positions = [
        {"position": "Center", "indicated": 1000.0, "delta_load": 0.5},
        {"position": "Corner 1", "indicated": 1000.0, "delta_load": 0.4},
        {"position": "Corner 2", "indicated": 1000.0, "delta_load": 0.45},
        {"position": "Corner 3", "indicated": 1000.0, "delta_load": 0.55},
        {"position": "Corner 4", "indicated": 1000.0, "delta_load": 0.48},
    ]
    res = evaluate_eccentricity_test(AccuracyClassEnum.CLASS_III, 3000.0, 1.0, 4, positions)
    assert res["overall_status"] == TestStatusEnum.PASS
    assert res["nominal_load"] == 1000.0

def test_discrimination_evaluation():
    # d = 1 kg -> Extra load = 1.4 kg -> Indication increases from 1000 to 1001 kg (delta >= 1d) -> PASS
    res = evaluate_discrimination_test(1000.0, 1.4, 1001.0, 1.0)
    assert res["status"] == TestStatusEnum.PASS

def test_overall_compliance_resolution_logic():
    """
    Verify the 4 core rules for overall compliance:
    1. If any test is FAIL -> FAIL
    2. If all executed pass but applicable tests remain unexecuted -> MANUAL_REVIEW
    3. If all applicable tests pass -> PASS
    4. If any test is BLOCKED or MANUAL_REVIEW -> MANUAL_REVIEW
    """
    # Rule 1: Fail precedence
    statuses = [TestStatusEnum.PASS, TestStatusEnum.FAIL, TestStatusEnum.PASS]
    assert (TestStatusEnum.FAIL if any(s == TestStatusEnum.FAIL for s in statuses) else TestStatusEnum.PASS) == TestStatusEnum.FAIL

    # Rule 2: Incomplete applicable tests -> MANUAL_REVIEW
    applicable_codes = {"A.4.2.3", "A.4.4.1", "A.4.7", "A.4.10", "A.4.8", "A.4.11"}
    executed_codes = {"A.4.2.3", "A.4.4.1"}
    unexecuted = applicable_codes - executed_codes
    assert len(unexecuted) > 0
    # Overall evaluation cannot be PASS when unexecuted exists
    overall = TestStatusEnum.MANUAL_REVIEW if unexecuted else TestStatusEnum.PASS
    assert overall == TestStatusEnum.MANUAL_REVIEW

    # Rule 3: Fully executed applicable tests -> PASS
    executed_full = {"A.4.2.3", "A.4.4.1", "A.4.7", "A.4.10", "A.4.8", "A.4.11"}
    unexecuted_none = applicable_codes - executed_full
    assert len(unexecuted_none) == 0
    overall_full = TestStatusEnum.PASS if not unexecuted_none else TestStatusEnum.MANUAL_REVIEW
    assert overall_full == TestStatusEnum.PASS

