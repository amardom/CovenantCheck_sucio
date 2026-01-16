import os
import json
from dotenv import load_dotenv
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

# 1. Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY not found in .env file. Please add it to run the AI Agent.")

def run_covenant_check():
    # 2. File paths based on your GitHub repository structure
    defs_path = "data/samples/definitions.txt"
    covs_path = "data/samples/covenants.txt"

    if not os.path.exists(defs_path) or not os.path.exists(covs_path):
        print(f"Error: Sample files not found at {defs_path} or {covs_path}")
        return

    # Read the contract segments
    with open(defs_path, "r", encoding="utf-8") as f:
        defs_text = f.read()
    with open(covs_path, "r", encoding="utf-8") as f:
        covs_text = f.read()

    print("--- Step 1: Extracting Logic with Google Gemini ---")
    agent = CovenantAIAgent(api_key=GEMINI_API_KEY)
    
    try:
        # The AI generates the JSON "Recipe"
        contract_logic = agent.generate_recipe(defs_text, covs_text)
        print("Logic successfully extracted:")
        print(json.dumps(contract_logic, indent=2))
    except Exception as e:
        print(f"Error during logic extraction: {e}")
        return

    print("\n--- Step 2: Configuring the Z3 Formal Engine ---")
    engine = CovenantCheckEngine()
    
    # Build the mathematical model based on the AI's recipe
    for step in contract_logic['recipe']:
        engine.add_logic_step(step)

    print("Z3 Engine loaded with contract logic.")

    # 3. CFO Manual Inputs (Simulating User Input)
    # NOTE: The keys in this dictionary must match the 'name' fields extracted by the AI.
    print("\n--- Step 3: Verifying Compliance (CFO Inputs) ---")
    
    # Example values designed to test the 10% EBITDA cap logic:
    cfo_inputs = {
        "operating_profit": 1000000,
        "interest_expense": 200000,
        "depreciation_and_amortization": 100000,
        "extraordinary_restructuring_costs": 500000, # This should trigger the 10% cap logic
        "gross_borrowings": 3500000,
        "cash": 500000
    }

    # 4. Execute the verification
    threshold = contract_logic['threshold']
    operator = contract_logic['operator']
    
    result = engine.verify(cfo_inputs, threshold, operator)

    print(f"\nFINAL VERDICT:")
    print(f"Contract Status: {result}")
    print(f"Covenant Threshold: {threshold} ({'Maximum' if operator == 'le' else 'Minimum'})")

if __name__ == "__main__":
    run_covenant_check()