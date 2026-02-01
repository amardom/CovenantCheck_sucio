import pytest
from app.core.postprocessing import calculate_stress_matrix

VALID_PORTFOLIO = {"Client1": {"history": {"2024": {"Q1": {"logics": [], "cfo_data": {}}}}}}
VALID_CLIENTS = ["Netflix"]
VALID_YEAR = "2026"
VALID_QUARTER = "Q1"

VALID_CONFIG = {
    "var_x": {"name": "ebitda", "direction": "down", "steps": 5, "max_pct": 0.5},
    "var_y": {"name": "euribor", "direction": "up", "steps": 5, "max_pct": 0.5}
}

@pytest.mark.parametrize("p, c, y, q, config, expected_msg", [
    ([], ["C1"], VALID_YEAR, VALID_QUARTER, VALID_CONFIG, "PORTFOLIO_NOT_DICT"),
    (VALID_PORTFOLIO, "NoLista", VALID_YEAR, VALID_QUARTER, VALID_CONFIG, "CLIENTS_NOT_LIST"),
    (VALID_PORTFOLIO, [], VALID_YEAR, VALID_QUARTER, VALID_CONFIG, "CLIENTS_LIST_EMPTY"),
    (VALID_PORTFOLIO, [123], VALID_YEAR, VALID_QUARTER, VALID_CONFIG, "CLIENT_NOT_STR"),
    (VALID_PORTFOLIO, VALID_CLIENTS, 2024, VALID_QUARTER, VALID_CONFIG, "YEAR_NOT_STR"),
    (VALID_PORTFOLIO, VALID_CLIENTS, "24", VALID_QUARTER, VALID_CONFIG, "YEAR_FORMAT_INVALID"),
    (VALID_PORTFOLIO, VALID_CLIENTS, VALID_YEAR, 1, VALID_CONFIG, "QUARTER_NOT_STR"),
    (VALID_PORTFOLIO, VALID_CLIENTS, VALID_YEAR, "Q5", VALID_CONFIG, "QUARTER_FORMAT_INVALID"),
    (VALID_PORTFOLIO, VALID_CLIENTS, VALID_YEAR, VALID_QUARTER, "NoDict", "STRESS_CONFIG_NOT_DICT"),
    
    (VALID_PORTFOLIO, VALID_CLIENTS, VALID_YEAR, VALID_QUARTER, {"var_y": {}}, "VAR_X_MISSING"),
    (VALID_PORTFOLIO, VALID_CLIENTS, VALID_YEAR, VALID_QUARTER, {"var_x": {}}, "VAR_Y_MISSING"),
])
def test_matrix_basic_assertions(p, c, y, q, config, expected_msg):
    with pytest.raises(AssertionError) as exc:
        calculate_stress_matrix(p, c, y, q, config)
    assert str(exc.value) == expected_msg

@pytest.mark.parametrize("target_key", ["var_x", "var_y"])
@pytest.mark.parametrize("patch, expected_msg", [
    ({"name": None}, "NAME_MISSING_IN_"),
    ({"name": 123}, "NAME_NOT_STR_IN_"),
    ({"name": ""}, "NAME_EMPTY_IN_"),
    ({"direction": None}, "DIRECTION_MISSING_IN_"),
    ({"direction": "flat"}, "DIRECTION_FORMAT_INVALID_IN_"),
    ({"direction": ""}, "DIRECTION_EMPTY_IN_"),
    ({"steps": None}, "STEPS_MISSING_IN_"),
    ({"steps": "5"}, "STEPS_NOT_INT_IN_"),
    ({"steps": 0}, "STEPS_IMPOSSIBLE_VALUE_IN_"),
    ({"max_pct": None}, "MAX_PCT_MISSING_IN_"),
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