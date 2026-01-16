from z3 import *
import json

class CovenantCheckEngine:
    def __init__(self):
        self.solver = Solver()
        self.vars = {}
        self.descriptions = {}  # Stores human-readable names for reporting

    def _get_var(self, name):
        """Creates or retrieves a Z3 Real variable."""
        if name not in self.vars:
            self.vars[name] = Real(name)
        return self.vars[name]

    def add_logic_step(self, step):
        """
        Translates a single logic 'recipe' into a Z3 constraint.
        Handles: Sums, Subtractions, and Relative Caps.
        """
        target = self._get_var(step['target'])
        
        # Pattern 1: Weighted Linear Combination (Sum/Sub/Cap)
        if 'components' in step:
            terms = []
            for comp in step['components']:
                val = self._get_var(comp['name'])
                weight = comp['weight']
                
                # Handle Relative Cap (e.g., "Max 10% of EBITDA")
                if 'cap_percentage' in comp:
                    ref_var = self._get_var(comp['cap_reference'])
                    limit = ref_var * comp['cap_percentage']
                    # The term is: weight * min(actual_value, percentage_of_reference)
                    term = weight * If(val > limit, limit, val)
                
                # Handle Absolute Cap (e.g., "Max $100,000")
                elif 'cap_absolute' in comp:
                    limit = comp['cap_absolute']
                    term = weight * If(val > limit, limit, val)
                
                else:
                    term = weight * val
                
                terms.append(term)
            
            self.solver.add(target == Sum(terms))

        # Pattern 2: Division (The Ratio)
        elif step.get('op') == 'div':
            numerator = self._get_var(step['args'][0])
            denominator = self._get_var(step['args'][1])
            # Prevent Division by Zero errors in the solver
            self.solver.add(denominator != 0)
            self.solver.add(target == numerator / denominator)

    def verify_compliance(self, input_data, covenant_limit, operator='le'):
        """
        Injects CFO inputs and checks if the threshold is breached.
        operator 'le' = Less than or equal (Standard for Leverage)
        operator 'ge' = Greater than or equal (Standard for Interest Cover)
        """
        self.solver.push()  # Create a checkpoint
        
        # Inject manual data from CFO
        for var_name, value in input_data.items():
            self.solver.add(self._get_var(var_name) == value)
            
        final_ratio = self._get_var("FINAL_RATIO")
        
        # Define what a 'Breach' looks like
        if operator == 'le':
            is_breach = final_ratio > covenant_limit
        else:
            is_breach = final_ratio < covenant_limit
            
        self.solver.add(is_breach)
        
        result = self.solver.check()
        
        report = {}
        if result == sat:
            model = self.solver.model()
            # Convert Z3 fraction to float
            calculated = model[final_ratio].as_decimal(4).replace('?', '')
            report = {
                "status": "BREACH",
                "value": float(calculated),
                "threshold": covenant_limit,
                "margin": 0.0
            }
        else:
            # If no breach is possible, the status is compliant
            report = {
                "status": "COMPLIANT",
                "value": "Safe",
                "threshold": covenant_limit
            }
            
        self.solver.pop()  # Reset the solver for the next check
        return report

    def get_headroom(self, input_data, target_variable, covenant_limit):
        """
        PhD Level Feature: Calculates how much a variable (e.g. EBITDA) 
        can drop before the contract is breached.
        """
        # Logic: Find the value of target_variable that makes FINAL_RATIO == covenant_limit
        self.solver.push()
        for var_name, value in input_data.items():
            if var_name != target_variable:
                self.solver.add(self._get_var(var_name) == value)
        
        self.solver.add(self._get_var("FINAL_RATIO") == covenant_limit)
        
        if self.solver.check() == sat:
            m = self.solver.model()
            break_point = m[self._get_var(target_variable)].as_decimal(2)
            self.solver.pop()
            return break_point
        
        self.solver.pop()
        return None