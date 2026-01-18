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

    contexto_eval = {**vars, **z3_helpers} # Dictionary for eval().

    print(f"----- Z3 AUDIT: {logic_json.get('contract_name')} -----\n")

    # 3. Load rules.
    for i, rule in enumerate(logic_json['logical_conditions']):
        try:
            formula_z3 = eval(rule['formula'], {"__builtins__": None}, contexto_eval)
            print(f"DEBUG - Rule #{i+1}: {formula_z3}\n")
            s.add(formula_z3)
        except Exception as e:
            print(f"⚠️ Error en Regla {rule['id']}: {e}\n")

    # 4. Load CFO data.
    for name, value in cfo_inputs.items():
        if name in vars:
            s.add(vars[name] == float(value))

    # 5. Verify logics.
    result = s.check()
    
    if result == sat:
        print("STATUS: ✅ COMPLIANT (SAT)")
        m = s.model()
        for v in vars:
            if v not in ['If', 'And', 'Or']:
                val = m[vars[v]]
                # Fraction to decimal.
                decimal = float(val.as_decimal(2).replace('?', '')) if hasattr(val, 'as_decimal') else val
                print(f"  > {v:.<50} {decimal}")
    else:
        print("STATUS: ❌ NON-COMPLIANT OR CONFLICT (UNSAT)")
        print("CFO has violated a constraint or the data is inconsistent.\n")

    missing = [v for v in vars if v not in cfo_inputs and v not in ['If', 'And', 'Or', 'Max', 'Min']]
    if missing:
        print(f"💡 NOTE: The variables {missing} have been automatically calculated to satisfy the agreement.\n")
