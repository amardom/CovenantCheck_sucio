from z3 import *

class CovenantCheckEngine:
    def __init__(self):
        self.solver = Solver()
        self.vars = {}

    def _get_var(self, name):
        if name not in self.vars:
            self.vars[name] = Real(name)
        return self.vars[name]

    def add_logic_step(self, step):
        target = self._get_var(step['target'])
        
        if 'components' in step:
            terms = []
            for comp in step['components']:
                val = self._get_var(comp['name'])
                weight = comp['weight']
                
                # Matches the 'enum' we forced in the AI schema
                if comp.get('cap_type') == 'relative':
                    ref_var = self._get_var(comp['cap_reference'])
                    limit = ref_var * comp['cap_percentage']
                    # The Circular Logic
                    term = weight * If(val > limit, limit, val)
                else:
                    term = weight * val
                terms.append(term)
            
            self.solver.add(target == Sum(terms))

        elif step.get('op') == 'div':
            num = self._get_var(step['args'][0])
            den = self._get_var(step['args'][1])
            self.solver.add(den != 0)
            self.solver.add(target == num / den)

    def verify(self, inputs, threshold, operator):
        self.solver.push()
        
        # Inject CFO values
        for name, val in inputs.items():
            self.solver.add(self._get_var(name) == val)
        
        final_ratio = self._get_var("FINAL_RATIO")
        
        # Check for breach
        if operator == 'le':
            is_breach = final_ratio > threshold
        else:
            is_breach = final_ratio < threshold
            
        self.solver.add(is_breach)
        result = self.solver.check()
        
        self.solver.pop()
        return "BREACH" if result == sat else "COMPLIANT"