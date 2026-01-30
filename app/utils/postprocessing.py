from z3 import *
from app.core.z3_engine import verify_logics

def find_max_stress(portfolio, clients, year, quarter, target_var, step, direction):

    assert isinstance(clients, list), "CLIENTS_NOT_A_LIST" 
    assert len(clients) > 0, "CLIENTS_LIST_EMPTY"
    assert all(isinstance(c, str) for c in clients), "CLIENT_NOT_A_STR"
    assert isinstance(year, str), "YEAR_NOT_A_STR"
    assert len(year) == 4, "YEAR_FORMAT_INVALID"
    assert isinstance(quarter, str), "QUARTER_NOT_A_STR"
    assert quarter in ["Q1", "Q2", "Q3", "Q4"], "QUARTER_FORMAT_INVALID"

    stress_analysis = {}
    
    for client in clients:

        current_drop = 0.0
        is_safe = True

        while is_safe == True and current_drop < 1.0:
            
            logics = portfolio[client].history[year][quarter]["logics"]
            cfo_data = portfolio[client].history[year][quarter]["cfo_data"]
            
            factor = (1 - current_drop) if direction == "down" else (1 + current_drop)
            test_data = cfo_data.copy()
            test_data[target_var] = cfo_data[target_var] * factor
            
            z3_result = verify_logics(logics, test_data)
            print(f"DEBUG {client}: Drop {current_drop} -> Result: {z3_result['is_compliant']}")
            if z3_result["is_compliant"] == True:
                print(f"DEBUG {client}: Drop {current_drop} -> Result: {z3_result['is_compliant']}")
                current_drop = current_drop + step
            else:
                is_safe = False

        last_sat = max(0, current_drop - step)
        max_allowed_drop = last_sat * 100
        last_sat_factor = (1 - last_sat) if direction == "down" else (1 + last_sat)
        break_value = cfo_data[target_var] * last_sat_factor

        stress_analysis[client] = {
            "target_var" : target_var,
            "year_quarter" : f"{year}_{quarter}",
            "current_value" : cfo_data[target_var],
            "headroom_pct": f"{max_allowed_drop:.1f}%",
            "limit_value": round(break_value, 2),
            "status": "Safe" if max_allowed_drop > 9 else "Critical"
        }

    return stress_analysis

def calculate_stress_matrix(portfolio, clients, year, quarter, var_config):
    """
    var_config = {
        "var_x": {"name": "ebitda", "direction": "down", "steps": 5, "max_pct": 0.5},
        "var_y": {"name": "euribor", "direction": "up", "steps": 5, "max_pct": 1.0}
    }
    """
    matrix_results = {}

    for client in clients:
        logics = portfolio[client].history[year][quarter]["logics"]
        cfo_data = portfolio[client].history[year][quarter]["cfo_data"]
        
        conf_x = var_config["var_x"]
        conf_y = var_config["var_y"]

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
        
        matrix_results[client] = {
            "grid": grid,
            "metadata": {
                "var_x": conf_x["name"],
                "var_y": conf_y["name"],
                "labels_x": [f"-{p*100:.0f}%" if conf_x["direction"]=="down" else f"+{p*100:.0f}%" for p in range_x],
                "labels_y": [f"-{p*100:.0f}%" if conf_y["direction"]=="down" else f"+{p*100:.0f}%" for p in range_y]
            }
        }
        
    return matrix_results