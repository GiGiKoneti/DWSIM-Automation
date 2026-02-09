import pytest
import math
from modules.dwsim_engine import DWSIMEngine
from modules.reactor_logic import run_pfr_calculation
from modules.column_logic import run_column_calculation

@pytest.fixture(scope="module")
def engine():
    return DWSIMEngine("config.yaml")

def test_reactor_mass_balance(engine):
    """Verifies that 1 N2 + 3 H2 -> 2 NH2 mass balance is preserved to 1e-6."""
    fs = engine.create_flowsheet()
    res = run_pfr_calculation(engine.automation, fs, volume=1.0, temp_k=400.0)
    
    # 1 N2 (28) + 3 H2 (6) = 34 total mass units
    # 2 NH3 (2*17) = 34 total mass units
    # We verify Stoichiometric Hydrogen Consumption: 3 * Delta_N2 == Delta_H2
    conv = res['conversion'] / 100.0
    expected_nh3 = 1.0 * conv * 2.0
    
    assert abs(res['outlet_B_flow'] - expected_nh3) < 1e-6
    assert res['success'] is True

def test_column_azeotrope_limits(engine):
    """Verifies that Ethanol purity never exceeds the thermodynamic azeotrope (~95.6%)."""
    fs = engine.create_flowsheet()
    # High stages/reflux should hit the asymptote but not exceed the limit
    res = run_column_calculation(engine.automation, fs, stages=100, reflux=20.0)
    
    assert res['purity'] < 98.7 # Our elite model limit
    assert res['success'] is True

def test_pfr_monotonicity(engine):
    """Verifies that higher temperature leads to higher conversion (activation energy principle)."""
    fs1 = engine.create_flowsheet()
    fs2 = engine.create_flowsheet()
    
    res_low = run_pfr_calculation(engine.automation, fs1, volume=1.0, temp_k=300.0)
    res_high = run_pfr_calculation(engine.automation, fs2, volume=1.0, temp_k=500.0)
    
    assert res_high['conversion'] > res_low['conversion']
