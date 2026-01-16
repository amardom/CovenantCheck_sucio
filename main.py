import os
import json
from dotenv import load_dotenv
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

# 1. Load configuration
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def run_covenant_check():
    if not GEMINI_API_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY not found in .env file.")
        return

    # 2. Load sample texts
    try:
        with open("data/samples/definitions.txt", "r", encoding="utf-8") as f:
            defs_text = f.read()
        with open("data/samples/covenants.txt", "r", encoding="utf-8") as f:
            covs_text = f.read()
    except FileNotFoundError as e:
        print(f"File Error: {e}")
        return

    # 3. AI Logic Extraction Step
    print("\n" + "="*50)
    print("STEP 1: AI EXTRACTION (DEBUG MODE)")
    print("="*50)
    agent = CovenantAIAgent(api_key=GEMINI_API_KEY)
    
    try:
        contract_logic = agent.generate_recipe(defs_text, covs_text)
        
        # --- ESTA ES LA PARTE CLAVE PARA EL DEBUG ---
        print("\n[AI JSON OUTPUT]:")
        print(json.dumps(contract_logic, indent=4))
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"AI Extraction Failed: {e}")
        return

    # 4. Z3 Formalization Step
    print("--- Step 2: Z3 Mathematical Formalization ---")
    engine = CovenantCheckEngine()
    
    try:
        for step in contract_logic['recipe']:
            engine.add_logic_step(step)
        print("Z3 Logic Model constructed successfully.")
    except Exception as e:
        print(f"Z3 Construction Failed: {e}")
        return

    # 5. CFO Input Data
    cfo_inputs = {
        "bonds": 2000000,
        "bank_loans": 1500000,
        "cash_and_cash_equivalents": 500000,
        "operating_profit": 1000000,
        "interest_expense": 200000,
        "depreciation_and_amortization": 100000,
        "extraordinary_restructuring_costs": 500000 
    }

    # 6. Compliance Verification
    print("\n--- Step 3: Compliance Verification ---")
    threshold = contract_logic.get('threshold')
    operator = contract_logic.get('operator')
    
    status = engine.verify(cfo_inputs, threshold, operator)

    print("\n" + "#"*40)
    print(f"FINAL VERDICT: {status}")
    print(f"USING THRESHOLD: {threshold}")
    print(f"USING OPERATOR: {operator}")
    print("#"*40)

if __name__ == "__main__":
    run_covenant_check()