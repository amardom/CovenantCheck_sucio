from z3 import *

def validate_json(logics):

    assert isinstance(logics, dict), "LOGICS_NOT_A_DICT"
    
    assert "audit_id" in logics, "AUDIT_ID_IS_MISSING"
    assert isinstance(logics["audit_id"], str), "AUDIT_ID_NOT_STR"
    assert len(logics["audit_id"]) > 0, "AUDIT_ID_IS_EMPTY"
    
    assert "contract_name" in logics, "CONTRACT_NAME_IS_MISSING"
    assert isinstance(logics["contract_name"], str), "CONTRACT_NAME_NOT_STR"
    assert len(logics["contract_name"]) > 0, "CONTRACT_NAME_IS_EMPTY"

    assert "variables" in logics, "VARIABLES_IS_MISSING"
    assert len(logics["variables"]) > 0, "VARIABLES_IS_EMPTY"
    
    for var in logics["variables"]:
        assert "name" in var, "NAME_IS_MISSING"
        assert "definition" in var, "DEFINITION_IS_MISSING"
        assert "definition_page" in var, "DEFINITION_PAGE_IS_MISSING"

        assert isinstance(var["name"], str), "NAME_NOT_STR"
        assert isinstance(var["definition"], str), "DEFINITION_NOT_STR"
        assert isinstance(var["definition_page"], int), "DEFINITION_PAGE_NOT_INT"

        assert len(var["name"]) > 0, "NAME_IS_EMPTY"
        assert len(var["definition"]) > 0, "DEFINITION_IS_EMPTY"
        assert var["definition_page"] > 0, "DEFINITION_PAGE_IS_BELOW_ONE"

    for var in logics["logical_conditions"]:
        assert "id" in var, "ID_IS_MISSING"
        assert "formula" in var, "FORMULA_IS_MISSING"
        assert "evidence" in var, "EVIDENCE_IS_MISSING"
        assert "evidence_page" in var, "EVIDENCE_PAGE_IS_MISSING"

        assert isinstance(var["id"], int), "ID_NOT_INT"
        assert isinstance(var["formula"], str), "FORMULA_NOT_STR"
        assert isinstance(var["evidence"], str), "EVIDENCE_NOT_STR"
        assert isinstance(var["evidence_page"], int), "EVIDENCE_PAGE_NOT_INT"

        assert var["id"] > 0, "ID_IS_BELOW_ONE"
        assert len(var["formula"]) > 0, "FORMULA_IS_EMPTY"
        assert len(var["evidence"]) > 0, "EVIDENCE_IS_EMPTY"
        assert var["evidence_page"] > 0, "EVIDENCE_PAGE_IS_BELOW_ONE"

    var_names = [v["name"] for v in logics["variables"]]
    assert len(var_names) == len(set(var_names)), "DUPLICATES_IN_VARIABLES"

    logic_ids = [l["id"] for l in logics["logical_conditions"]]
    assert len(logic_ids) == len(set(logic_ids)), "DUPLICATES_IN_LOGICAL_CONDITIONS"

    print(f"logics validated.")

def verify_logics(logics, cfo_data):

    validate_json(logics)

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
        assert is_expr(formula_z3), "Z3_EXPRESSION_INVALID"
        print(f"Rule #{rule['id']}: {formula_z3}")
        s.assert_and_track(formula_z3, f"RULE_{rule['id']}")

    # 4. Load CFO data.
    for name, value in cfo_data.items():
        assert isinstance(value, (int, float)), "CFO_DATA_VAR_INVALID"
        if name in vars:
            s.assert_and_track(vars[name] == RealVal(str(value)), f"DATA_{name}")

    # 5. Verify logics.
    result = s.check()
    assert result != unknown, "RESULT_UNKNOWN"

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

        print("STATUS: ✅ COMPLIANT (SAT).")
        
        m = s.model()
        response["model"] = m
      
        for var_name in vars:

            var_obj = vars[var_name]
            z3_val = m[var_obj]
            
            assert z3_val is not None, "Z3_VALUE_IS_NONE"
            
            val_float = float(z3_val.as_decimal(2).replace('?', '')) if hasattr(z3_val, 'as_decimal') else z3_val
            values = values + [val_float]
            response["calculated_values"][var_name] = val_float
            print(f"  > {var_name:.<50} {val_float}")

    elif result == unsat:

        print("STATUS: ❌ NON-COMPLIANT OR CONFLICT (UNSAT - BREACH).")

        core = s.unsat_core()
        for label in core:
            label_str = str(label)
            if label_str.startswith("DATA_"):
                response["conflict_variables"].append(label_str.replace("DATA_", ""))
            elif label_str.startswith("RULE_"):
                response["conflict_rules"].append(label_str.replace("RULE_", ""))

        if response["conflict_variables"]:
            vars_str = ", ".join(response["conflict_variables"])
            print(f"Variables causing conflict: {vars_str}.")
        
        if response["conflict_rules"]:
            rules_str = ", ".join(response["conflict_rules"])
            print(f"Broken rules (IDs): {rules_str}.")

    missing = [v for v in vars if v not in cfo_data]
    if missing:
        
        response["missing"] = missing
        print(f"NOTE: The variables {missing} have been automatically calculated to satisfy the agreement.")

    norm_metric = math.sqrt(sum(v**2 for v in values))/math.pi
    response["norm_metric"] = norm_metric

    return response