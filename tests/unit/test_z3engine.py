import json
import pytest
from app.core.z3_engine import verify_logics

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def test_all_scenarios():
    
    scenarios = [
        ("logic_data_pass_simple.json","cfo_data_pass_simple.json", True),
        ("logic_data_pass_complex.json","cfo_data_pass_complex.json", True),
        ("logic_data_pass_complex.json","cfo_data_pass_complex_fail.json", False)
    ]

    print(f"\n--- INICIANDO BUCLE DE PRUEBAS ---")

    for filename_logic, filename_cfo, expected in scenarios:

        path_logic_data = f"tests/scenarios/{filename_logic}"
        logic_data = load_json(path_logic_data)
        path_cfo_data = f"tests/scenarios/{filename_cfo}"
        cfo_data = load_json(path_cfo_data)
        
        result = verify_logics(logic_data, cfo_data)
        
        print(f"Testing {filename_logic}: Expected {expected} -> Got {result['is_compliant']}")
        
        assert result["is_compliant"] == expected, f"Error en {filename_logic}: No coincide el resultado."