import pytest
from app.core.postprocessing import calculate_stress_matrix

# Mock inicial de datos válidos para que el test no falle por otros motivos
valid_portfolio = {"Client1": {"history": {"2024": {"Q1": {"logics": [], "cfo_data": {}}}}}}
valid_config = {
    "var_x": {"name": "ebitda", "direction": "down", "steps": 5, "max_pct": 0.5},
    "var_y": {"name": "euribor", "direction": "up", "steps": 5, "max_pct": 0.5}
}

@pytest.mark.parametrize("p, c, y, q, config, expected_msg", [
    # Validaciones de estructura principal
    ([], ["C1"], "2024", "Q1", valid_config, "PORTFOLIO_NOT_A_DICT"), # (Debería ser NOT_A_DICT según tu código, ojo)
    ({}, "NoLista", "2024", "Q1", valid_config, "CLIENTS_NOT_A_LIST"),
    ({}, [], "2024", "Q1", valid_config, "CLIENTS_LIST_EMPTY"),
    ({}, [123], "2024", "Q1", valid_config, "CLIENT_NOT_A_STR"),
    ({}, ["C1"], 2024, "Q1", valid_config, "YEAR_NOT_A_STR"),
    ({}, ["C1"], "24", "Q1", valid_config, "YEAR_FORMAT_INVALID"),
    ({}, ["C1"], "2024", 1, valid_config, "QUARTER_NOT_A_STR"),
    ({}, ["C1"], "2024", "Q5", valid_config, "QUARTER_FORMAT_INVALID"),
    ({}, ["C1"], "2024", "Q1", "NoDict", "STRESS_CONFIG_NOT_A_DICT"),
    
    ({}, ["C1"], "2024", "Q1", {"var_y": {}}, "VAR_X_IS_MISSING"),
    ({}, ["C1"], "2024", "Q1", {"var_x": {}}, "VAR_Y_IS_MISSING"),
])
def test_matrix_basic_assertions(p, c, y, q, config, expected_msg):
    with pytest.raises(AssertionError) as exc:
        calculate_stress_matrix(p, c, y, q, config)
    assert str(exc.value) == expected_msg

@pytest.mark.parametrize("target_key", ["var_x", "var_y"])
@pytest.mark.parametrize("patch, expected_msg", [
    ({"name": None}, "NAME_IS_MISSING_IN_"),
    ({"name": 123}, "NAME_NOT_STR_IN_"),
    ({"name": ""}, "NAME_IS_EMPTY_IN_"),
    ({"direction": None}, "DIRECTION_IS_MISSING_IN_"),
    ({"direction": "flat"}, "DIRECTION_FORMAT_INVALID_IN_"),
    ({"direction": ""}, "DIRECTION_IS_EMPTY_IN_"),
    ({"steps": None}, "STEPS_IS_MISSING_IN_"),
    ({"steps": "5"}, "STEPS_NOT_INT_IN_"),
    ({"steps": 0}, "STEPS_IMPOSSIBLE_VALUE_IN_"),
    ({"max_pct": None}, "MAX_PCT_IS_MISSING_IN_"),
    ({"max_pct": "0.5"}, "MAX_PCT_NOT_FLOAT_IN_"),
    ({"max_pct": 2.0}, "MAX_PCT_IMPOSSIBLE_VALUE_IN_")
])
def test_matrix_config_details(target_key, patch, expected_msg):
    # Creamos una config válida y saboteamos solo un campo
    test_config = {
        "var_x": {"name": "rev", "direction": "down", "steps": 5, "max_pct": 0.5},
        "var_y": {"name": "opex", "direction": "up", "steps": 5, "max_pct": 0.5}
    }
    
    # Aplicamos el sabotaje
    for k, v in patch.items():
        if v is None: del test_config[target_key][k]
        else: test_config[target_key][k] = v

    with pytest.raises(AssertionError) as exc:
        calculate_stress_matrix({}, ["C1"], "2024", "Q1", test_config)
    
    assert expected_msg in str(exc.value)
    assert target_key in str(exc.value)