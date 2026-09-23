from typing import List, Dict, Any
from app.models import AccuracyClassEnum, TestStatusEnum
from app.calculations.mpe import calculate_mpe_for_load
from app.calculations.weighing import calculate_error_changeover, calculate_corrected_error

def evaluate_eccentricity_test(
    accuracy_class: AccuracyClassEnum,
    max_capacity: float,
    e_val: float,
    num_support_points: int,
    positions: List[Dict[str, Any]], # [{"position": "Center", "indicated": 1000.0, "delta_load": 0.2}, ...]
    zero_error: float = 0.0,
    in_service: bool = False
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.4.7: Eccentricity tests.
    
    Test load:
    - For <= 4 support points: L = 1/3 (Max + Tare) [Cl. A.4.7.1]
    - For > 4 support points: L = 1 / (N - 1) * (Max + Tare) [Cl. A.4.7.2]
    
    Criterion:
    The errors at each position (corrected for zero error) shall not exceed
    the maximum permissible error for the applied test load:
    |E_c,i| = |E_i - E_0| <= MPE(L_ecc)
    """
    if num_support_points <= 4:
        nominal_load = round(max_capacity / 3.0, 3)
    else:
        nominal_load = round(max_capacity / (num_support_points - 1), 3)

    mpe = calculate_mpe_for_load(accuracy_class, nominal_load, e_val, in_service)

    evaluated_positions = []
    overall_pass = True

    for p in positions:
        pos_name = p.get("position", "Unknown Position")
        ind = p.get("indicated", nominal_load)
        dl = p.get("delta_load", 0.0)
        # Load can be explicit or defaulted to nominal
        applied_load = p.get("test_load", nominal_load)
        
        err = calculate_error_changeover(ind, applied_load, e_val, dl)
        c_err = calculate_corrected_error(err, zero_error)
        margin = round(mpe - abs(c_err), 6)
        status = TestStatusEnum.PASS if abs(c_err) <= (mpe + 1e-9) else TestStatusEnum.FAIL
        
        if status == TestStatusEnum.FAIL:
            overall_pass = False

        evaluated_positions.append({
            "position": pos_name,
            "applied_load": applied_load,
            "indicated": ind,
            "delta_load": dl,
            "error": err,
            "corrected_error": c_err,
            "mpe": mpe,
            "margin": margin,
            "status": status
        })

    return {
        "nominal_load": nominal_load,
        "num_support_points": num_support_points,
        "mpe": mpe,
        "zero_error_used": zero_error,
        "positions": evaluated_positions,
        "overall_status": TestStatusEnum.PASS if overall_pass else TestStatusEnum.FAIL,
        "formula": "L_ecc = Max / (N-1) or Max/3;  |Ec,i| <= MPE(L_ecc)",
        "clause": "OIML R 76-1:2006 Cl. A.4.7",
    }
