from z3 import *

def validate_json(logics):

    _ = logics['source_file']
    _ = logics['contract_name']

    for v in logics['variables']:
        _ = v['name']
        
    for rule in logics['logical_conditions']:
        _ = rule['id']
        _ = rule['formula']
        _ = rule['evidence']
    
    print("json validated.")

def verify_logics(logics, cfo_data):

    validate_json(logics)
    
    print(f"----- Z3 ENGINE: {logics.get('contract_name')} -----\n")

    # 1. Create the solver.
    s = Solver()
    s.set(unsat_core=True)
    
    # 2. Declare variables dynamically as Real.
    vars = {v['name']: Real(v['name']) for v in logics['variables']}

    z3_helpers = {
        'abs': lambda x: If(x >= 0, x, -x),
        'max': lambda a, b: If(a > b, a, b),
        'min': lambda a, b: If(a < b, a, b),
        'And': And,
        'Or': Or,
        'If': If
    }

    context_eval = {**vars, **z3_helpers} # Dictionary for eval().

    # 3. Load rules.
    for i, rule in enumerate(logics['logical_conditions']):
        formula_z3 = eval(rule['formula'], {"__builtins__": None}, context_eval)
        print(f"Rule #{rule['id']}: {formula_z3}\n")
        s.assert_and_track(formula_z3, f"RULE_{rule['id']}")

    # 4. Load CFO data.
    for name, value in cfo_data.items():
        if name in vars:
            s.assert_and_track(vars[name] == RealVal(str(value)), f"DATA_{name}")

    # 5. Verify logics.
    result = s.check()
    
    response = {
        "status": str(result).upper(),
        "is_compliant": result == z3.sat,
        "calculated_values": {},
        "model": None,
        "missing": {},
        "norm_metric" : 0,
        "conflict_variables": [],
        "conflict_rules": []
    }

    values = []
    if result == sat:

        print("STATUS: ✅ COMPLIANT (SAT)")
        
        m = s.model()
        response["model"] = m
      
        for var_name in vars:

            var_obj = vars[var_name]
            z3_val = m[var_obj]
            
            if z3_val is not None:
                
                val_float = float(z3_val.as_decimal(2).replace('?', '')) if hasattr(z3_val, 'as_decimal') else z3_val
                values = values + [val_float]
                response["calculated_values"][var_name] = val_float
                print(f"  > {var_name:.<50} {val_float}")

    elif result == unsat:

        print("STATUS: ❌ NON-COMPLIANT OR CONFLICT (UNSAT - BREACH)")

        core = s.unsat_core()
        for label in core:
            label_str = str(label)
            if label_str.startswith("DATA_"):
                response["conflict_variables"].append(label_str.replace("DATA_", ""))
            elif label_str.startswith("RULE_"):
                response["conflict_rules"].append(label_str.replace("RULE_", ""))

        if response["conflict_variables"]:
            vars_str = ", ".join(response["conflict_variables"])
            print(f"👉 Variables causing conflict: {vars_str}.")
        
        if response["conflict_rules"]:
            rules_str = ", ".join(response["conflict_rules"])
            print(f"👉 Broken rules (IDs): {rules_str}.\n")

    missing = [v for v in vars if v not in cfo_data]
    if missing:
        
        response["missing"] = missing
        print(f"💡 NOTE: The variables {missing} have been automatically calculated to satisfy the agreement.\n")

    norm_metric = math.sqrt(sum(v**2 for v in values))/math.pi
    response["norm_metric"] = norm_metric

    return response