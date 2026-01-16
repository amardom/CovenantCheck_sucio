import json
from app.core.z3_engine import CovenantCheckEngine

# Load the AI-generated recipe
with open('data/samples/contract_logic_v1.json', 'r') as f:
    contract_data = json.load(f)

engine = CovenantCheckEngine()

# 1. Build the mathematical model from the JSON recipe
for step in contract_data['recipe']:
    engine.add_logic_step(step)

# 2. These are the values the CFO types into your web form
cfo_inputs = {
    "gross_loans": 5000000,
    "bonds_outstanding": 2000000,
    "cash_on_hand": 500000,
    "net_income": 1200000,
    "interest_expense": 200000,
    "tax_expense": 100000,
    "depreciation_and_amortization": 300000,
    "extraordinary_restructuring_costs": 400000 
}

# 3. Run the verification
result = engine.verify_compliance(
    cfo_inputs, 
    contract_data['threshold'], 
    contract_data['operator']
)

print(f"Compliance Result: {result}")