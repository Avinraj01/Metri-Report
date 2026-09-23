from typing import Dict, Any
from app.models import AccuracyClassEnum, TestStatusEnum
from app.calculations.mpe import calculate_mpe_for_load

def evaluate_creep_test(
    accuracy_class: AccuracyClassEnum,
    max_capacity: float,
    e_val: float,
    i_0_min: float,   # Initial indication immediately after loading Max
    i_15_min: float,  # Indication after 15 min
    i_30_min: float   # Indication after 30 min
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.4.11.1: Creep test.
    1. The difference between the indication obtained immediately after loading
       and the indication observed during 30 min shall not exceed 0.5 MPE (or |MPE|).
       |I(30) - I(0)| <= |MPE(Max)|
    2. The difference between 15 min and 30 min shall not exceed 0.5 e:
       |I(30) - I(15)| <= 0.5 e
    """
    mpe_max = calculate_mpe_for_load(accuracy_class, max_capacity, e_val)
    
    total_creep_30m = round(abs(i_30_min - i_0_min), 6)
    interval_creep_15_30m = round(abs(i_30_min - i_15_min), 6)
    
    limit_interval = round(0.5 * e_val, 6)
    
    pass_total = total_creep_30m <= (mpe_max + 1e-9)
    pass_interval = interval_creep_15_30m <= (limit_interval + 1e-9)
    
    overall_status = TestStatusEnum.PASS if (pass_total and pass_interval) else TestStatusEnum.FAIL

    return {
        "i_0_min": i_0_min,
        "i_15_min": i_15_min,
        "i_30_min": i_30_min,
        "total_creep_30m": total_creep_30m,
        "mpe_max_limit": mpe_max,
        "pass_total": pass_total,
        "interval_creep_15_30m": interval_creep_15_30m,
        "limit_interval_0_5e": limit_interval,
        "pass_interval": pass_interval,
        "status": overall_status,
        "formula": "|I(30) - I(0)| <= MPE(Max) and |I(30) - I(15)| <= 0.5e",
        "clause": "OIML R 76-1:2006 Cl. A.4.11.1",
    }

def evaluate_zero_return_test(
    e_val: float,
    indicated_unloaded_15s: float,
    delta_load_unloaded: float = 0.0
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.4.11.2: Zero return test.
    The deviation in zero reading before loading and 15 seconds after removal of load
    shall not exceed 0.5 e:
    |E_0_return| <= 0.5 e
    """
    p_zero_return = indicated_unloaded_15s + 0.5 * e_val - delta_load_unloaded
    err_zero_return = round(p_zero_return, 6) # zero load reference is 0
    limit = round(0.5 * e_val, 6)
    margin = round(limit - abs(err_zero_return), 6)
    status = TestStatusEnum.PASS if abs(err_zero_return) <= (limit + 1e-9) else TestStatusEnum.FAIL

    return {
        "indicated_unloaded_15s": indicated_unloaded_15s,
        "delta_load_unloaded": delta_load_unloaded,
        "error_zero_return": err_zero_return,
        "limit": limit,
        "margin": margin,
        "status": status,
        "formula": "|E0_return| <= 0.5e (within 15 seconds of unloading)",
        "clause": "OIML R 76-1:2006 Cl. A.4.11.2",
    }
