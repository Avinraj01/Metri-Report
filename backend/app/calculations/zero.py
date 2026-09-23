from typing import Dict, Any
from app.models import TestStatusEnum

def evaluate_zero_setting_accuracy(
    indicated_zero: float,
    e_val: float,
    delta_load_zero: float = 0.0,
    zero_load: float = 0.0
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.4.2.3: Accuracy of zero-setting
    The error at zero:
    E0 = I0 + 0.5e - delta_L0 - L0
    Acceptance criterion:
    |E0| <= 0.25 e
    """
    p_zero = indicated_zero + 0.5 * e_val - delta_load_zero
    e_zero = round(p_zero - zero_load, 6)
    limit = round(0.25 * e_val, 6)
    margin = round(limit - abs(e_zero), 6)
    status = TestStatusEnum.PASS if abs(e_zero) <= (limit + 1e-9) else TestStatusEnum.FAIL

    return {
        "indicated_zero": indicated_zero,
        "delta_load_zero": delta_load_zero,
        "zero_error": e_zero,
        "limit": limit,
        "limit_in_e": 0.25,
        "margin": margin,
        "status": status,
        "formula": "E0 = I0 + 0.5e - ΔL0 - L0;  |E0| <= 0.25e",
        "clause": "OIML R 76-1:2006 Cl. A.4.2.3",
    }

def evaluate_zero_setting_range(
    max_zero_positive: float,
    max_zero_negative: float,
    max_capacity: float
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause 4.5.1 / A.4.2.1: Range of zero-setting
    Total range as % of Max.
    Standard: -1% to +3% or +-2% of Max.
    """
    total_range = abs(max_zero_positive) + abs(max_zero_negative)
    percent_of_max = round((total_range / max_capacity) * 100.0, 3)
    
    # Standard typical limits: 4% total range
    limit_percent = 4.0
    status = TestStatusEnum.PASS if percent_of_max <= limit_percent else TestStatusEnum.FAIL
    
    return {
        "max_zero_positive": max_zero_positive,
        "max_zero_negative": max_zero_negative,
        "total_range": total_range,
        "percent_of_max": percent_of_max,
        "limit_percent": limit_percent,
        "status": status,
        "formula": "Range% = (Max_pos + |Max_neg|) / Max * 100",
        "clause": "OIML R 76-1:2006 Cl. 4.5.1 & A.4.2.1",
    }
