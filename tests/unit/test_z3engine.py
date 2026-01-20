import json
import pytest
from app.utils.integrity_json import validate_json
from app.core.z3_engine import verify_logics

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def test_sat_scenarios():
    
    scenarios = [
        ("logics_pass_simple.json","cfo_data_pass_simple.json", True, 13085595.147, ['consolidated_ebitda', 
                                                                                         'consolidated_total_net_debt', 
                                                                                         'consolidated_total_net_leverage_ratio']),
        ("logics_pass_complex.json","cfo_data_pass_complex.json", True, 15493715.317, {})
    ]

    print(f"\n--- INITIALIZING SAT TESTING LOOP ---")

    for filename_logic, filename_cfo, expected_sat_unsat, expected_norm_metric, expected_missing in scenarios:

        path_logic_data = f"tests/scenarios/{filename_logic}"
        logic_data = load_json(path_logic_data)
        validate_json(filename_logic, logic_data)

        path_cfo_data = f"tests/scenarios/{filename_cfo}"
        cfo_data = load_json(path_cfo_data)
        
        result = verify_logics(logic_data, cfo_data)
        
        print(f"Testing {filename_logic}: Expected {expected_sat_unsat} -> Got {result['is_compliant']}")
        assert result["is_compliant"] == expected_sat_unsat, f"Error in {filename_logic}: Result does not match."

        print(f"Testing {filename_logic}: Expected {expected_norm_metric} -> Got {result['norm_metric']}")
        assert result["norm_metric"] == pytest.approx(expected_norm_metric), f"Error in {filename_logic}: Result does not match."

        print(f"Testing {filename_logic}: Expected {expected_missing} -> Got {result['missing']}")
        assert result["missing"] == expected_missing, f"Error in {filename_logic}: Result does not match."

def test_unsat_scenarios():
    
    scenarios = [
        ("logics_pass_complex.json","cfo_data_pass_complex_fail.json", False, ['consolidated_total_net_leverage_ratio', 
                                                                                   'unrestricted_cash'], )
    ]

    print(f"\n--- INITIALIZING UNSAT TESTING LOOP ---")

    for filename_logic, filename_cfo, expected_sat_unsat, expected_conflict_variables in scenarios:

        path_logic_data = f"tests/scenarios/{filename_logic}"
        logic_data = load_json(path_logic_data)
        validate_json(filename_logic, logic_data)

        path_cfo_data = f"tests/scenarios/{filename_cfo}"
        cfo_data = load_json(path_cfo_data)
        
        result = verify_logics(logic_data, cfo_data)
        
        print(f"Testing {filename_logic}: Expected {expected_sat_unsat} -> Got {result['is_compliant']}")
        assert result["is_compliant"] == expected_sat_unsat, f"Error in {filename_logic}: Result does not match."

        print(f"Testing {filename_logic}: Expected {expected_conflict_variables} -> Got {result['conflict_variables']}")
        assert set(result["conflict_variables"]) == set(expected_conflict_variables), f"Error in {filename_logic}: Result does not match."

def test_verify_logics_unknown_should_fail():
    """
    Forzamos un UNKNOWN usando una fórmula no lineal compleja.
    Esto disparará el 'assert result != unknown'.
    """
    logics_complex = {
        "source_file": "complex_math.json",
        "contract_name": "Complexity Test",
        "variables": [{"name": "x", "context": "Non-linear math"}],
        "logical_conditions": [{
            "id": 999, 
            # x elevado a x es muy difícil para el solver de Reales estándar
            "formula": "x**x == 50", 
            "evidence": "Complexity breach", 
            "page": 1
        }]
    }
    
    # cfo_data vacío porque la variable x es la que causará el problema
    cfo_data = {}

    # El test pasa si el motor lanza un AssertionError por el resultado UNKNOWN
    with pytest.raises(AssertionError):
        verify_logics(logics_complex, cfo_data)