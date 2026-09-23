from typing import Dict, Any
from app.models import AccuracyClassEnum, TestStatusEnum
from app.calculations.mpe import calculate_mpe_for_load

def calculate_error_changeover(indicated: float, load: float, e_val: float, delta_load: float = 0.0) -> float:
    """
    OIML R 76-1:2006 Clause A.4.4.3:
    Exact indication prior to rounding:
    P = I + 0.5e - delta_L
    Error:
    E = P - L = I + 0.5e - delta_L - L
    """
    p_indicated = indicated + 0.5 * e_val - delta_load
    error = p_indicated - load
    return round(error, 6)

def calculate_corrected_error(error: float, zero_error: float = 0.0) -> float:
    """
    OIML R 76-1:2006 Clause A.4.4.3:
    Corrected error:
    E_c = E - E_0
    """
    return round(error - zero_error, 6)

def evaluate_weighing_point(
    accuracy_class: AccuracyClassEnum,
    load: float,
    indicated: float,
    e_val: float,
    delta_load: float = 0.0,
    zero_error: float = 0.0,
    in_service: bool = False
) -> Dict[str, Any]:
    """
    Evaluates an individual weighing observation point against OIML R 76-1:2006 Cl. A.4.4.1 & A.4.4.3.
    """
    error = calculate_error_changeover(indicated, load, e_val, delta_load)
    corrected_error = calculate_corrected_error(error, zero_error)
    mpe = calculate_mpe_for_load(accuracy_class, load, e_val, in_service)
    
    # Margin = MPE - |E_c|
    margin = round(mpe - abs(corrected_error), 6)
    status = TestStatusEnum.PASS if abs(corrected_error) <= (mpe + 1e-9) else TestStatusEnum.FAIL

    return {
        "load": load,
        "indicated": indicated,
        "delta_load": delta_load,
        "error": error,
        "corrected_error": corrected_error,
        "zero_error_used": zero_error,
        "mpe": mpe,
        "margin": margin,
        "status": status,
        "formula": "E = I + 0.5e - ΔL - L;  Ec = E - E0",
        "clause": "OIML R 76-1:2006 Cl. A.4.4.1 & A.4.4.3",
    }
