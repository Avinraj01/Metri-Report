from typing import Dict, Any
from app.models import TestStatusEnum

def evaluate_discrimination_test(
    initial_indicated: float,
    extra_load_applied: float, # must be approx 1.4 * d
    final_indicated: float,
    d_val: float
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.4.8 & Clause 3.8: Discrimination test.
    An additional load equal to 1.4 * d, when placed gently on the load receptor,
    shall produce an increase in indication of at least 1.0 * d.
    delta_I = I_final - I_initial >= 1.0 * d
    """
    min_required_extra_load = round(1.4 * d_val, 6)
    delta_indication = round(final_indicated - initial_indicated, 6)
    min_required_increase = round(1.0 * d_val, 6)
    
    # Check if extra load applied was sufficient
    extra_load_valid = extra_load_applied >= (min_required_extra_load - 1e-6)
    
    passed = extra_load_valid and (delta_indication >= (min_required_increase - 1e-9))
    status = TestStatusEnum.PASS if passed else TestStatusEnum.FAIL
    
    return {
        "initial_indicated": initial_indicated,
        "extra_load_applied": extra_load_applied,
        "min_required_extra_load": min_required_extra_load,
        "final_indicated": final_indicated,
        "delta_indication": delta_indication,
        "min_required_increase": min_required_increase,
        "status": status,
        "formula": "ΔI = I_final - I_initial >= 1d (with ΔL = 1.4d)",
        "clause": "OIML R 76-1:2006 Cl. A.4.8 & Cl. 3.8",
    }
