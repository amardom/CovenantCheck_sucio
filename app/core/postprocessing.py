from z3 import *
from app.core.z3_engine import verify_logics

def calculate_stress_matrix(portfolio, clients, year, quarter, stress_config):

    assert isinstance(portfolio, dict), "PORTFOLIO_NOT_DICT"

    assert isinstance(clients, list), "CLIENTS_NOT_LIST" 
    assert len(clients) > 0, "CLIENTS_LIST_EMPTY"
    assert all(isinstance(c, str) for c in clients), "CLIENT_NOT_STR"
    assert isinstance(year, str), "YEAR_NOT_STR"
    assert len(year) == 4, "YEAR_FORMAT_INVALID"
    assert isinstance(quarter, str), "QUARTER_NOT_STR"
    assert quarter in ["Q1", "Q2", "Q3", "Q4"], "QUARTER_FORMAT_INVALID"
    assert isinstance(stress_config, dict), "STRESS_CONFIG_NOT_DICT"
    
    assert "var_x" in stress_config, "VAR_X_MISSING"
    assert "var_y" in stress_config, "VAR_Y_MISSING"

    for key in ["var_x", "var_y"]:

        var = stress_config[key]

        assert "name" in var, f"NAME_MISSING_IN_{key}"
        assert "direction" in var, f"DIRECTION_MISSING_IN_{key}"
        assert "steps" in var, f"STEPS_MISSING_IN_{key}"
        assert "max_pct" in var, f"MAX_PCT_MISSING_IN_{key}"
    
        assert isinstance(var["name"], str), f"NAME_NOT_STR_IN_{key}"
        assert isinstance(var["direction"], str), f"DIRECTION_NOT_STR_IN_{key}"
        assert isinstance(var["steps"], int), f"STEPS_NOT_INT_IN_{key}"
        assert isinstance(var["max_pct"], float), f"MAX_PCT_NOT_FLOAT_IN_{key}"

        assert len(var["name"]) > 0, f"NAME_EMPTY_IN_{key}"
        assert len(var["direction"]) > 0, f"DIRECTION_EMPTY_IN_{key}"
        assert var["direction"] in ["down", "up"], f"DIRECTION_FORMAT_INVALID_IN_{key}"
        assert var["steps"] > 0 and var["steps"] < 21, f"STEPS_IMPOSSIBLE_VALUE_IN_{key}"
        assert var["max_pct"] > 0.001 and var["max_pct"] < 1.001, f"MAX_PCT_IMPOSSIBLE_VALUE_IN_{key}"

    matrix_results = {}

    for client in clients:
        logics = portfolio[client].history[year][quarter]["logics"]
        cfo_data = portfolio[client].history[year][quarter]["cfo_data"]
        
        conf_x = stress_config["var_x"]
        conf_y = stress_config["var_y"]

        # Generamos los rangos de estrés (ej: 0.0, 0.1, 0.2...)
        range_x = [i * (conf_x["max_pct"] / conf_x["steps"]) for i in range(conf_x["steps"] + 1)]
        range_y = [i * (conf_y["max_pct"] / conf_y["steps"]) for i in range(conf_y["steps"] + 1)]

        grid = []
        for drop_y in range_y:
            row = []
            for drop_x in range_x:
                test_data = cfo_data.copy()
                
                # Aplicar estrés Variable X
                factor_x = (1 - drop_x) if conf_x["direction"] == "down" else (1 + drop_x)
                test_data[conf_x["name"]] = cfo_data[conf_x["name"]] * factor_x
                
                # Aplicar estrés Variable Y
                factor_y = (1 - drop_y) if conf_y["direction"] == "down" else (1 + drop_y)
                test_data[conf_y["name"]] = cfo_data[conf_y["name"]] * factor_y
                
                # Verificación Z3
                z3_res = verify_logics(logics, test_data)
                
                row.append({
                    "val_x": test_data[conf_x["name"]],
                    "val_y": test_data[conf_y["name"]],
                    "pct_x": drop_x,
                    "pct_y": drop_y,
                    "is_compliant": z3_res["is_compliant"]
                })
            grid.append(row)
        
        # Buscamos el último índice 'True' en la fila donde Y = 0%
        last_safe_x = max([i for i, cell in enumerate(grid[0]) if cell["is_compliant"]], default=0)
        headroom_x = range_x[last_safe_x] * 100

        # Buscamos el último índice 'True' en la columna donde X = 0%
        last_safe_y = max([i for i, r in enumerate(grid) if r[0]["is_compliant"]], default=0)
        headroom_y = range_y[last_safe_y] * 100

        matrix_results[client] = {
            "grid": grid,
            f"headroom_x": f"{headroom_x:.1f}%",
            f"headroom_y": f"{headroom_y:.1f}%",
            "metadata": {
                "var_x": conf_x["name"],
                "var_y": conf_y["name"],
                "labels_x": [f"-{p*100:.0f}%" if conf_x["direction"]=="down" else f"+{p*100:.0f}%" for p in range_x],
                "labels_y": [f"-{p*100:.0f}%" if conf_y["direction"]=="down" else f"+{p*100:.0f}%" for p in range_y]
            }
        }
        
    return matrix_results