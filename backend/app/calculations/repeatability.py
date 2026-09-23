from typing import List, Dict, Any
from app.models import AccuracyClassEnum, TestStatusEnum
from app.calculations.mpe import calculate_mpe_for_load
from app.calculations.weighing import calculate_error_changeover

def evaluate_repeatability_series(
    accuracy_class: AccuracyClassEnum,
    load: float,
    e_val: float,
    readings: List[Dict[str, float]], # [{"indicated": x, "delta_load": y}, ...]
    in_service: bool = False
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause A.4.10 & Clause 3.6.1: Repeatability test.
    The difference between the maximum and minimum results obtained in
    a series of weighings with the same load shall not exceed the absolute
    value of the maximum permissible error for that load:
    delta_E = E_max - E_min <= |MPE(L)|
    """
    if not readings or len(readings) < 3:
        return {
            "status": TestStatusEnum.NOT_TESTED,
            "error_msg": "At least 3 weighings required for repeatability evaluation (Cl. A.4.10).",
            "clause": "OIML R 76-1:2006 Cl. A.4.10"
        }

    errors = []
    for r in readings:
        ind = r.get("indicated", 0.0)
        dl = r.get("delta_load", 0.0)
        err = calculate_error_changeover(ind, load, e_val, dl)
        errors.append(err)

    max_err = max(errors)
    min_err = min(errors)
    repeatability_range = round(max_err - min_err, 6)
    mpe = calculate_mpe_for_load(accuracy_class, load, e_val, in_service)
    margin = round(mpe - repeatability_range, 6)
    status = TestStatusEnum.PASS if repeatability_range <= (mpe + 1e-9) else TestStatusEnum.FAIL

    return {
        "load": load,
        "runs_count": len(readings),
        "errors": errors,
        "max_error": max_err,
        "min_error": min_err,
        "repeatability_range": repeatability_range,
        "mpe": mpe,
        "margin": margin,
        "status": status,
        "formula": "ΔE = E_max - E_min <= |MPE(L)|",
        "clause": "OIML R 76-1:2006 Cl. A.4.10 & 3.6.1",
    }
