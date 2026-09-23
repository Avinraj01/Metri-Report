import pytest
from app.models import AccuracyClassEnum
from app.calculations.mpe import get_mpe_in_e, calculate_mpe_for_load

def test_class_iii_mpe_tiers():
    # Class III (OIML R 76-1 Table 6):
    # 0 <= m <= 500 e -> 0.5e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 0) == 0.5
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 500) == 0.5
    # 500 < m <= 2000 e -> 1.0e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 501) == 1.0
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 2000) == 1.0
    # 2000 < m <= 10000 e -> 1.5e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 2001) == 1.5
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 10000) == 1.5

def test_class_ii_mpe_tiers():
    # Class II (Table 6):
    # 0 <= m <= 5000 e -> 0.5e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_II, 5000) == 0.5
    # 5000 < m <= 20000 e -> 1.0e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_II, 15000) == 1.0
    # 20000 < m <= 100000 e -> 1.5e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_II, 50000) == 1.5

def test_class_i_mpe_tiers():
    # Class I (Table 6):
    # 0 <= m <= 50000 e -> 0.5e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_I, 50000) == 0.5
    # 50000 < m <= 200000 e -> 1.0e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_I, 100000) == 1.0
    # > 200000 e -> 1.5e
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_I, 250000) == 1.5

def test_in_service_mpe_doubled():
    # Clause 3.5.2: In-service verification MPE is doubled
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 500, in_service=True) == 1.0
    assert get_mpe_in_e(AccuracyClassEnum.CLASS_III, 1000, in_service=True) == 2.0

def test_calculate_mpe_for_load_physical_units():
    # For e = 0.5 kg, load = 500 kg (1000 e -> tier 2 = 1.0 e -> 0.5 kg)
    mpe_kg = calculate_mpe_for_load(AccuracyClassEnum.CLASS_III, 500.0, e_val=0.5)
    assert mpe_kg == 0.5
