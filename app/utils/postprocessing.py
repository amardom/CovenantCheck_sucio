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

"""
def run_stress_test(logics, cfo_data, stress_factors):

    #stress_factors: {"ebitda": 0.9, "interest_rate": 1.2}

    stressed_data = cfo_data.copy()
    
    for var, factor in stress_factors.items():
        if var in stressed_data:
            stressed_data[var] = stressed_data[var] * factor

    z3_result = verify_logics(logics, stressed_data)
    return z3_result
"""