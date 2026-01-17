from z3 import *

def auditor_z3_pro(logic_json, cfo_inputs):
    # 1. Crear el Solver
    s = Solver()
    
    # 2. Declarar variables dinámicamente como Reales
    # Agregamos 'If' al diccionario para que eval() lo reconozca en las fórmulas
    vars = {v['name']: Real(v['name']) for v in logic_json['variables']}
    vars['If'] = If  
    vars['And'] = And
    vars['Or'] = Or

    print(f"--- Z3 AUDIT: {logic_json.get('contract_name')} ---")

    # 3. Cargar Reglas (Identidades y Covenants)
    for rule in logic_json['logical_conditions']:
        try:
            # Reemplazamos '==' por '=' si es necesario para Z3 eval
            # Pero en Python eval, '==' es correcto para comparaciones
            formula_z3 = eval(rule['formula'], {"__builtins__": None}, vars)
            s.add(formula_z3)
        except Exception as e:
            print(f"⚠️ Error en Regla {rule['id']}: {e}")

    # 4. Cargar Inputs del CFO
    for name, value in cfo_inputs.items():
        if name in vars:
            s.add(vars[name] == float(value))

    # 5. Verificación
    result = s.check()
    
    if result == sat:
        print("ESTADO: ✅ CUMPLIMIENTO (SAT)")
        m = s.model()
        # Imprimir resultados numéricos finales
        for v in vars:
            if v not in ['If', 'And', 'Or']:
                val = m[vars[v]]
                # Conversión estética de fracción a decimal
                decimal = float(val.as_decimal(2).replace('?', '')) if hasattr(val, 'as_decimal') else val
                print(f"  > {v:.<30} {decimal}")
    else:
        print("ESTADO: ❌ INCUMPLIMIENTO O CONFLICTO (UNSAT)")
        print("El CFO ha violado una restricción o los datos son inconsistentes.")
