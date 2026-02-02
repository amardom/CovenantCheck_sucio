import json
import pytest
from app.core.z3_engine import verify_logics

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
        path_cfo_data = f"tests/scenarios/{filename_cfo}"
        cfo_data = load_json(path_cfo_data)
        
        result = verify_logics(logic_data, cfo_data)
        
        assert result["is_compliant"] == expected_sat_unsat, f"Error in {filename_logic}: Result does not match."
        assert result["norm_metric"] == pytest.approx(expected_norm_metric), f"Error in {filename_logic}: Result does not match."
        assert result["missing"] == expected_missing, f"Error in {filename_logic}: Result does not match."

def test_verify_logics_unsat_scenarios():
    
    scenarios = [
        ("logics_complex.json","cfo_data_complex_fail.json", False, ['consolidated_total_net_leverage_ratio', 
                                                                                   'unrestricted_cash'], )
    ]

    for filename_logic, filename_cfo, expected_sat_unsat, expected_conflict_variables in scenarios:

        path_logic_data = f"tests/scenarios/{filename_logic}"
        logic_data = load_json(path_logic_data)
        path_cfo_data = f"tests/scenarios/{filename_cfo}"
        cfo_data = load_json(path_cfo_data)
        
        result = verify_logics(logic_data, cfo_data)
        
        assert result["is_compliant"] == expected_sat_unsat, f"Error in {filename_logic}: Result does not match."
        assert set(result["conflict_variables"]) == set(expected_conflict_variables), f"Error in {filename_logic}: Result does not match."

def test_verify_logics_unknown():
    logics = {
        "audit_id": "ClientAlpha_2026_Q1.json",
        "contract_name": "Complexity Test",
        "variables": [{"name": "x", "definition": "Non-linear math", "definition_page": 9}],
        "logical_conditions": [{
            "id": 999, 
            "formula": "x**x == 50",
            "evidence": "Complexity breach", 
            "evidence_page": 1
        }]
    }
    
    cfo_data = {}

    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, cfo_data)
    assert str(exc.value) == "RESULT_UNKNOWN"
    print(f"ERROR: {exc.value}")

def test_verify_logics_missing_model_value():
    logics = {
        "audit_id": "ClientAlpha_2026_Q1.json",
        "contract_name": "Orphan Test",
        "variables": [
            {"name": "x", "definition": "Active", "definition_page": 9},
            {"name": "y", "definition": "Orphan variable (missing within the eqs or data)", "definition_page": 19}
        ],
        "logical_conditions": [{
            "id": 1, 
            "formula": "x > 10", 
            "evidence": "Test", 
            "evidence_page": 1
        }]
    }
    
    cfo_data = {"x": 15.0}

    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, cfo_data)
    assert str(exc.value) == "Z3_VALUE_IS_NONE"
    print(f"ERROR: {exc.value}")

def test_verify_logics_invalid_z3_expression():
    logics = {
        "audit_id": "ClientAlpha_2026_Q1",
        "contract_name": "Invalid Z3 Expression Test",
        "variables": [{"name": "ebitda", "definition": "Finance", "definition_page": 9}],
        "logical_conditions": [{
            "id": 101,
            "formula": "1 == 1", 
            "evidence": "Static check", 
            "evidence_page": 1
        }]
    }
    
    cfo_data = {"ebitda": 100.0}

    # Z3 will fail since '1 == 1' returns True (bool), and is_expr(True) is False.
    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, cfo_data)
    assert str(exc.value) == "Z3_EXPRESSION_INVALID"
    print(f"ERROR: {exc.value}")

def test_verify_logics_bad_cfo_data():
    logics = {
        "audit_id": "ClientAlpha_2026_Q1",
        "contract_name": "Complexity Test",
        "variables": [{"name": "x", "definition": "Test bad cfo_data", "definition_page": 9},
                    {"name": "y", "definition": "Test bad cfo_data", "definition_page": 10}],
        "logical_conditions": [{
            "id": 9, 
            "formula": "x+y == 5",
            "evidence": "Very simple equation",
            "evidence_page": 1
        }]
    }

    bad_cfo_data = {
        "revenue": 1000000.0,
        "debt": "500000.0",
        "x": True,
        "y": None,
        "observations": "N/A"
    }

    with pytest.raises(AssertionError) as exc:
        verify_logics(logics, bad_cfo_data)
    assert str(exc.value) == "CFO_DATA_VAR_INVALID"
    print(f"ERROR: {exc.value}")
    