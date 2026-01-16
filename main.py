from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

# 1. Load your raw text files
with open("data/samples/definitions.txt", "r") as f:
    defs = f.read()
with open("data/samples/covenants.txt", "r") as f:
    covs = f.read()

# 2. Extract Logic via AI
agent = CovenantAIAgent(api_key="your_api_key_here")
contract_logic = agent.generate_recipe(defs, covs)

# 3. Initialize Z3 Engine
engine = CovenantCheckEngine()
for step in contract_logic['recipe']:
    engine.add_logic_step(step)

# 4. Manual Input from CFO (The "CovenantCheck_sucio" UI data)
# In reality, these names come from the AI's recipe.
cfo_data = {
    "operating_profit": 1000000,
    "interest_expense": 200000,
    "depreciation_and_amortization": 100000,
    "extraordinary_restructuring_costs": 500000, # This is > 10% of the total!
    "gross_borrowings": 4000000,
    "cash": 500000
}

# 5. The Verdict
status = engine.verify(cfo_data, contract_logic['threshold'], contract_logic['operator'])
print(f"Contract Status: {status}")