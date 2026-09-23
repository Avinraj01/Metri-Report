from typing import Dict, Any
from app.models import AccuracyClassEnum, TestStatusEnum

def evaluate_temp_effect_on_no_load(
    accuracy_class: AccuracyClassEnum,
    e_val: float,
    t1: float, # Temp 1 in °C
    zero_error_t1: float,
    t2: float, # Temp 2 in °C
    zero_error_t2: float
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.5.3.2: Temperature effect on no-load indication.
    The zero indication or near-zero indication shall not vary by more than:
    - 1 e per 5 °C for Class II, III, IIII
    - 1 e per 1 °C for Class I
    """
    delta_t = abs(t2 - t1)
    if delta_t == 0:
        return {
            "status": TestStatusEnum.NOT_TESTED,
            "error_msg": "Temperature difference ΔT must be greater than 0 °C.",
            "clause": "OIML R 76-1:2006 Cl. A.5.3.2"
        }
    
    delta_zero = abs(zero_error_t2 - zero_error_t1)
    # Drift per 5°C or per 1°C
    if accuracy_class == AccuracyClassEnum.CLASS_I or str(accuracy_class) == "I":
        permissible_rate = (1.0 * e_val) / 1.0  # e per °C
        rate_unit = "1e / 1°C"
    else:
        permissible_rate = (1.0 * e_val) / 5.0  # e per 5°C
        rate_unit = "1e / 5°C"
    
    actual_rate = round(delta_zero / delta_t, 6)
    status = TestStatusEnum.PASS if actual_rate <= (permissible_rate + 1e-9) else TestStatusEnum.FAIL

    return {
        "t1": t1,
        "zero_error_t1": zero_error_t1,
        "t2": t2,
        "zero_error_t2": zero_error_t2,
        "delta_t": delta_t,
        "delta_zero": delta_zero,
        "actual_drift_rate": actual_rate,
        "permissible_rate": round(permissible_rate, 6),
        "rate_unit": rate_unit,
        "status": status,
        "formula": "|E0(T2) - E0(T1)| / |T2 - T1| <= 1e / 5°C (or 1e / 1°C for Class I)",
        "clause": "OIML R 76-1:2006 Cl. A.5.3.2",
    }

def evaluate_voltage_variation(
    nominal_voltage: float,
    applied_voltage: float,
    zero_error: float,
    e_val: float
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.5.4: Voltage variations.
    Mains: Unom - 15% to Unom + 10%.
    Zero drift must not exceed 0.25 e.
    """
    limit = round(0.25 * e_val, 6)
    status = TestStatusEnum.PASS if abs(zero_error) <= (limit + 1e-9) else TestStatusEnum.FAIL
    
    return {
        "nominal_voltage": nominal_voltage,
        "applied_voltage": applied_voltage,
        "zero_error": zero_error,
        "limit": limit,
        "status": status,
        "formula": "|E0(U)| <= 0.25e at Unom - 15% and Unom + 10%",
        "clause": "OIML R 76-1:2006 Cl. A.5.4",
    }
