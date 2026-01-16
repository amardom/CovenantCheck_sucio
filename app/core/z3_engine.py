from z3 import *

class CovenantCheckEngine:
    def __init__(self):
        self.solver = Solver()
        self.vars = {}

    def _get_var(self, name):
        """Standardizes variable creation in Z3."""
        if name not in self.vars:
            self.vars[name] = Real(name)
        return self.vars[name]

    def add_logic_step(self, step):
        target = self._get_var(step['target'])
        
        # 1. Summation Logic (with Cap Support)
        if step.get('op') == 'sum':
            terms = []
            for comp in step['components']:
                val = self._get_var(comp['name'])
                weight = comp['weight']
                
                if comp.get('cap_type') == 'relative':
                    ref_var = self._get_var(comp['cap_reference'])
                    # Handle 10% vs 0.1 logic
                    percentage = comp.get('cap_percentage', 0)
                    if percentage > 1:
                        percentage = percentage / 100
                    
                    limit = ref_var * percentage
                    # Z3 'If' handles the cap logic mathematically
                    term = weight * If(val > limit, limit, val)
                else:
                    term = weight * val
                terms.append(term)
            self.solver.add(target == Sum(terms))

        # 2. Division Logic (for Final Ratio)
        elif step.get('op') == 'div':
            num = self._get_var(step['args'][0])
            den = self._get_var(step['args'][1])
            # PhD Constraint: Ensure mathematical validity
            self.solver.add(den != 0)
            self.solver.add(target == num / den)

    def verify(self, inputs, threshold, operator):
        """This is the method your main.py was missing!"""
        self.solver.push() # Save state
        
        # A. Bind input values
        for name, val in inputs.items():
            var = self._get_var(name)
            self.solver.add(var == val)
            
        # B. Important: Bounding Logic
        # Prevent Z3 from exploring impossible negative values
        for var in self.vars.values():
            self.solver.add(var > -1000000000) 

        final_ratio = self._get_var("final_ratio")
        
        # C. Define Breach Condition
        if operator == 'le':
            # Compliant if <= threshold, so Breach if >
            breach_condition = final_ratio > threshold
        else:
            # Compliant if >= threshold, so Breach if <
            breach_condition = final_ratio < threshold
            
        self.solver.add(breach_condition)
        
        result = self.solver.check()
        
        # D. Optional: Debugging the Math
        if result == sat:
            print("\n[Z3 Solver Proof - How it found a Breach]:")
            model = self.solver.model()
            # Sort variables for readability
            for d in sorted(model.decls(), key=lambda x: x.name()):
                print(f"  {d.name()} = {model[d]}")

        self.solver.pop() # Reset state for next run
        
        # In Z3: sat means it found a breach. unsat means NO breach is possible.
        return "BREACH" if result == sat else "COMPLIANT"