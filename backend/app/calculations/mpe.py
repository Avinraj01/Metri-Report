from typing import Tuple
from app.models import AccuracyClassEnum

def get_mpe_in_e(accuracy_class: AccuracyClassEnum, load_in_e: float, in_service: bool = False) -> float:
    """
    Determines Maximum Permissible Error (MPE) in units of 'e'
    as per OIML R 76-1:2006 (E) Clause 3.5.1, Table 6.
    
    Tier limits:
    - Class I:
        0 <= m <= 50,000 e       -> +-0.5 e
        50,000 < m <= 200,000 e  -> +-1.0 e
        m > 200,000 e            -> +-1.5 e
        
    - Class II:
        0 <= m <= 5,000 e        -> +-0.5 e
        5,000 < m <= 20,000 e    -> +-1.0 e
        20,000 < m <= 100,000 e  -> +-1.5 e
        
    - Class III:
        0 <= m <= 500 e          -> +-0.5 e
        500 < m <= 2,000 e       -> +-1.0 e
        2,000 < m <= 10,000 e    -> +-1.5 e
        
    - Class IIII:
        0 <= m <= 50 e           -> +-0.5 e
        50 < m <= 200 e          -> +-1.0 e
        200 < m <= 1,000 e       -> +-1.5 e
        
    For in-service verification (Clause 3.5.2), MPE is doubled.
    """
    m = abs(load_in_e)
    factor = 2.0 if in_service else 1.0

    if accuracy_class == AccuracyClassEnum.CLASS_I or str(accuracy_class) == "I":
        if m <= 50000:
            mpe = 0.5
        elif m <= 200000:
            mpe = 1.0
        else:
            mpe = 1.5
    elif accuracy_class == AccuracyClassEnum.CLASS_II or str(accuracy_class) == "II":
        if m <= 5000:
            mpe = 0.5
        elif m <= 20000:
            mpe = 1.0
        else:
            mpe = 1.5
    elif accuracy_class == AccuracyClassEnum.CLASS_III or str(accuracy_class) == "III":
        if m <= 500:
            mpe = 0.5
        elif m <= 2000:
            mpe = 1.0
        else:
            mpe = 1.5
    elif accuracy_class == AccuracyClassEnum.CLASS_IIII or str(accuracy_class) == "IIII":
        if m <= 50:
            mpe = 0.5
        elif m <= 200:
            mpe = 1.0
        else:
            mpe = 1.5
    else:
        # Default fallback if unknown class
        mpe = 1.0

    return mpe * factor

def calculate_mpe_for_load(accuracy_class: AccuracyClassEnum, load: float, e_val: float, in_service: bool = False) -> float:
    """
    Returns MPE converted to the actual physical unit (e.g. kg or g)
    MPE_unit = MPE_in_e * e_val
    """
    if e_val <= 0:
        raise ValueError("e_value must be positive")
    load_in_e = load / e_val
    mpe_e = get_mpe_in_e(accuracy_class, load_in_e, in_service)
    return round(mpe_e * e_val, 6)
