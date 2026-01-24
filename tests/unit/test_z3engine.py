import json
import pytest
from app.core.z3_engine import validate_json, verify_logics

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def test_verify_logics_sat_scenarios():
    
    scenarios = [
        ("logics_simple.json","cfo_data_simple.json", True, 13085595.147, ['consolidated_ebitda', 
                                                                                         'consolidated_total_net_debt', 
                                                                                         'consolidated_total_net_leverage_ratio']),
        ("logics_complex.json","cfo_data_complex.json", True, 15493715.317, {})
    ]

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

def test_verify_logics_unsat_scenarios():
    
    scenarios = [
        ("logics_complex.json","cfo_data_complex_fail.json", False, ['consolidated_total_net_leverage_ratio', 
                                                                                   'unrestricted_cash'], )
    ]

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

def test_verify_logics_unknown():
    logics = {
        "source_file": "complex_math.json",
        "contract_name": "Complexity Test",
        "variables": [{"name": "x", "context": "Non-linear math"}],
        "logical_conditions": [{
            "id": 999, 
            "formula": "x**x == 50", # Non-linear is complicated for z3 using Reals.
            "evidence": "Complexity breach", 
            "page": 1
        }]
    }
    
    cfo_data = {}

    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, cfo_data)
    assert str(exc.value) == "RESULT_UNKNOWN"
    print(f"ERROR: {exc.value}")

def test_verify_logics_missing_model_value():
    logics = {
        "source_file": "useless_var.json",
        "contract_name": "Orphan Test",
        "variables": [
            {"name": "x", "context": "Active"},
            {"name": "y", "context": "Orphan"} # Unused variable.
        ],
        "logical_conditions": [{
            "id": 1, 
            "formula": "x > 10", 
            "evidence": "Test", 
            "page": 1
        }]
    }
    
    cfo_data = {"x": 15}

    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, cfo_data)
    assert str(exc.value) == "Z3_VALUE_IS_NONE"
    print(f"ERROR: {exc.value}")

def test_verify_logics_not_a_z3_expr():
    logics = {
        "source_file": "invalid_z3_expression.json",
        "contract_name": "Invalid Expr Test",
        "variables": [{"name": "ebitda", "context": "Finance"}],
        "logical_conditions": [{
            "id": 101, 
            # Esto es un Booleano de Python, no una fórmula de Z3
            "formula": "1 == 1", 
            "evidence": "Static check", 
            "page": 1
        }]
    }
    
    cfo_data = {"ebitda": 100}

    # El motor debería partir porque '1 == 1' devuelve True (bool)
    # y is_expr(True) es Falso.
    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, cfo_data)
    assert str(exc.value) == "Z3_EXPRESSION_INVALID"
    print(f"ERROR: {exc.value}")

def test_verify_logics_bad_cfo_data():
    logics = {
        "source_file": "complex_math.json",
        "contract_name": "Complexity Test",
        "variables": [{"name": "x", "context": "Test bad cfo_data"},
                    {"name": "y", "context": "Test bad cfo_data"}],
        "logical_conditions": [{
            "id": 9, 
            "formula": "x+y == 5",
            "evidence": "Very simple equation",
            "page": 1
        }]
    }

    bad_cfo_data = {
        "revenue": 1000000.0,
        "debt": "500000",
        "x": True,
        "y": None,
        "observations": "N/A"
    }

    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, bad_cfo_data)
    assert str(exc.value) == "CFO_DATA_VAR_INVALID"
    print(f"ERROR: {exc.value}")
    