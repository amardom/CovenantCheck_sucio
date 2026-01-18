from z3 import *

def verify_logics(logic_json, cfo_inputs):

    # 1. Create the solver.
    s = Solver()
    
    # 2. Declare variables dynamically as Real.
    vars = {v['name']: Real(v['name']) for v in logic_json['variables']}

    z3_helpers = {
        'abs': lambda x: If(x >= 0, x, -x),
        'max': lambda a, b: If(a > b, a, b),
        'min': lambda a, b: If(a < b, a, b),
        'And': And,
        'Or': Or,
        'If': If
    }

    context_eval = {**vars, **z3_helpers} # Dictionary for eval().

    print(f"----- Z3 AUDIT: {logic_json.get('contract_name')} -----\n")

    # 3. Load rules.
    for i, rule in enumerate(logic_json['logical_conditions']):

        formula_z3 = eval(rule['formula'], {"__builtins__": None}, context_eval)
        print(f"Rule #{rule['id']}: {formula_z3}\n")
        s.add(formula_z3)

    # 4. Load CFO data.
    for name, value in cfo_inputs.items():
        if name in vars:
            s.add(vars[name] == float(value))

    # 5. Verify logics.
    result = s.check()
    
    response = {
        "status": str(result).upper(),
        "is_compliant": result == z3.sat,
        "calculated_values": {},
        "model": None,
        "missing": {}
    }

    if result == sat:

        print("STATUS: ✅ COMPLIANT (SAT)")
        
        m = s.model()
        response["model"] = m

        for var_name in vars:

            var_obj = vars[var_name]
            z3_val = m[var_obj]
            
            if z3_val is not None:
                
                val_float = float(z3_val.as_decimal(2).replace('?', '')) if hasattr(z3_val, 'as_decimal') else z3_val
                response["calculated_values"][var_name] = val_float
                
                print(f"  > {var_name:.<50} {val_float}")
    else:

        print("STATUS: ❌ NON-COMPLIANT OR CONFLICT (UNSAT)")
        print("CFO has violated a constraint or the data is inconsistent.\n")

    missing = [v for v in vars if v not in cfo_inputs]
    if missing:
        
        response["missing"] = missing
        print(f"💡 NOTE: The variables {missing} have been automatically calculated to satisfy the agreement.\n")

    return response
