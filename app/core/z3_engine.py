from z3 import *

class CovenantCheckEngine:
    def __init__(self):
        self.solver = Solver()
        self.vars = {}

    def get_var(self, name):
        """Returns a Z3 Real variable, creating it if it doesn't exist."""
        if name not in self.vars:
            self.vars[name] = Real(name)
        return self.vars[name]

    def add_logic(self, ai_output):
        """
        Dynamically builds the mathematical constraints in Z3 based on 
        the AI extracted parameters.
        """
        # Define core variables
        ebitda = self.get_var('adjusted_ebitda')
        debt = self.get_var('total_net_debt')
        ratio = self.get_var('final_ratio')

        ebitda_sum = 0
        debt_sum = 0

        # Process components and apply CAPs (like the 10% rule)
        for comp in ai_output['components']:
            var = self.get_var(comp['name'])
            
            # If the component has a dynamic cap (e.g., 10% of EBITDA)
            if comp.get('cap_percentage') and comp['cap_percentage'] > 0:
                # Determine which variable is the reference for the cap
                limit_ref = ebitda if comp['cap_reference'] == 'ebitda' else debt
                
                # Create an auxiliary variable for the capped value
                capped_val = Real(f"capped_{comp['name']}")
                
                # Logical Constraint: capped_val = MIN(actual_value, reference * percentage)
                self.solver.add(capped_val == If(var > limit_ref * comp['cap_percentage'], 
                                                limit_ref * comp['cap_percentage'], 
                                                var))
                current_val = capped_val
            else:
                current_val = var

            # Aggregate into the corresponding group
            if comp['group'] == 'ebitda':
                ebitda_sum += current_val * comp['weight']
            else:
                debt_sum += current_val * comp['weight']

        # Define the final relationships
        self.solver.add(ebitda == ebitda_sum)
        self.solver.add(debt == debt_sum)
        
        # Avoid division by zero by adding a constraint that EBITDA must be > 0
        self.solver.add(ebitda > 0)
        self.solver.add(ratio == debt / ebitda)

    def verify(self, inputs, threshold, operator):
        """
        Checks if the provided CFO inputs satisfy or breach the covenant.
        """
        self.solver.push()
        
        # Inject CFO input values
        # If a variable detected by the AI is missing in inputs, we default it to 0
        for var_name in self.vars:
            if var_name in inputs:
                self.solver.add(self.vars[var_name] == inputs[var_name])
            elif "capped_" not in var_name and var_name not in ['adjusted_ebitda', 'total_net_debt', 'final_ratio']:
                # Default unknown components to 0 to avoid arbitrary values from the solver
                self.solver.add(self.vars[var_name] == 0)

        # Define the BREACH condition
        # If operator is 'le' (less or equal), a breach happens if ratio > threshold
        if operator == 'le':
            self.solver.add(self.vars['final_ratio'] > threshold)
        elif operator == 'ge':
            self.solver.add(self.vars['final_ratio'] < threshold)

        # Check for a solution (SAT means a Breach was found)
        check_result = self.solver.check()
        
        if check_result == sat:
            result = "BREACH"
            print("\n[Z3 Solver Proof - Mathematical Model of the Breach]:")
            model = self.solver.model()
            # Sort and print the variables for clarity
            for d in sorted(model.decls(), key=lambda x: x.name()):
                print(f"  {d.name()} = {model[d]}")
        else:
            result = "COMPLIANT"
        
        self.solver.pop()
        return result