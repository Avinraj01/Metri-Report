from typing import List, Dict, Any
from app.models import TestStatusEnum

def evaluate_span_stability(
    e_val: float,
    baseline_error: float,
    subsequent_errors: List[float] # measurements recorded over testing cycles
) -> Dict[str, Any]:
    """
    OIML R 76-1:2006 Clause B.4: Span stability test.
    The error shall not vary by more than 0.5 e between any two measurements:
    |E_i - E_baseline| <= 0.5 e
    """
    limit = round(0.5 * e_val, 6)
    deviations = []
    overall_pass = True

    for i, err in enumerate(subsequent_errors):
        diff = round(abs(err - baseline_error), 6)
        passed = diff <= (limit + 1e-9)
        if not passed:
            overall_pass = False
        deviations.append({
            "run_index": i + 1,
            "measured_error": err,
            "span_deviation": diff,
            "passed": passed
        })

    status = TestStatusEnum.PASS if (overall_pass and len(subsequent_errors) > 0) else (
        TestStatusEnum.NOT_TESTED if len(subsequent_errors) == 0 else TestStatusEnum.FAIL
    )

    return {
        "baseline_error": baseline_error,
        "limit": limit,
        "runs_count": len(subsequent_errors),
        "deviations": deviations,
        "status": status,
        "formula": "|E_i - E_baseline| <= 0.5e (over span stability cycles)",
        "clause": "OIML R 76-1:2006 Cl. B.4",
    }
