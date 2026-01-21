from z3 import *

def validate_json(filename_logics, logics):

    assert isinstance(logics, dict)

    assert "source_file" in logics
    assert type(logics["source_file"]) is str and len(logics["source_file"]) > 0

    assert logics['source_file'] == filename_logics

    assert "contract_name" in logics
    assert type(logics["contract_name"]) is str and len(logics["contract_name"]) > 0

    assert "variables" in logics and len(logics["variables"]) > 0
    assert "logical_conditions" in logics and len(logics["logical_conditions"]) > 0

    for var in logics["variables"]:
        assert "name" in var
        assert "definition" in var
        assert "definition_page" in var

        assert type(var["name"]) is str and len(var["name"]) > 0
        assert type(var["definition"]) is str and len(var["definition"]) > 0
        assert type(var["definition_page"]) is int and var["definition_page"] > 0

    var_names = [v["name"] for v in logics["variables"]]
    assert len(var_names) == len(set(var_names))

    for var in logics["logical_conditions"]:
        assert "id" in var
        assert "formula" in var
        assert "evidence" in var
        assert "evidence_page" in var

        assert type(var["id"]) is int and var["id"] > 0
        assert type(var["formula"]) is str and len(var["formula"]) > 0
        assert type(var["evidence"]) is str and len(var["evidence"]) > 0
        assert type(var["evidence_page"]) is int and var["evidence_page"] > 0

    logic_ids = [l["id"] for l in logics["logical_conditions"]]
    assert len(logic_ids) == len(set(logic_ids))

    print("***JSON " + filename_logics + " VALIDATED***")

def verify_logics(logics, cfo_data):
    
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
        assert is_expr(formula_z3)
        print(f"Rule #{rule['id']}: {formula_z3}\n")
        s.assert_and_track(formula_z3, f"RULE_{rule['id']}")

    # 4. Load CFO data.
    for name, value in cfo_data.items():
        if name in vars:
            s.assert_and_track(vars[name] == RealVal(str(value)), f"DATA_{name}")

    # 5. Verify logics.
    result = s.check()
    assert result != unknown

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
            
            assert z3_val is not None
            
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