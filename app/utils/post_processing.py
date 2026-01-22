from z3 import *
from app.core.z3_engine import verify_logics

def run_stress_test(logics, cfo_data, stress_factors):

    #stress_factors: {"ebitda": 0.9, "interest_rate": 1.2}

    stressed_data = cfo_data.copy()
    
    for var, factor in stress_factors.items():
        if var in stressed_data:
            stressed_data[var] = stressed_data[var] * factor

    z3_result = verify_logics(logics, stressed_data)
    return z3_result

def find_max_stress(logics, cfo_data, target_var="ebitda", step=0.01):

    current_drop = 0.0
    is_safe = True
    
    while is_safe == True and current_drop < 1.0:
        
        test_data = cfo_data.copy()
        test_data[target_var] = cfo_data[target_var] * (1 - current_drop)
        
        z3_result = verify_logics(logics, test_data)

        if z3_result["is_compliant"] == z3.sat:
            current_drop = current_drop + step
        else:
            is_safe = False
            
    last_sat = (current_drop - step)
    max_allowed_drop = last_sat * 100
    break_value = cfo_data[target_var] * (1 - last_sat)
    
    return {
        "headroom_pct": f"{max_allowed_drop:.1f}%",
        "limit_value": break_value,
        "status": "Safe" if max_allowed_drop > 10 else "Critical"
    }