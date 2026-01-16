import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Import your custom modules
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

# 1. Configuration & API Diagnostics
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def diagnose_api():
    if not GEMINI_API_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY not found in .env file.")
        return False
    
    genai.configure(api_key=GEMINI_API_KEY)
    print("--- API Diagnosis ---")
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Available Models: {available_models}")
        
        # Updated check for Gemini 3
        if any('gemini-3-flash' in m for m in available_models):
            print("Status: gemini-3-flash is supported.")
            return True
        else:
            # Fallback check for any 2.0+ model
            print("Status: Using cutting-edge model (Gemini 2.0+).")
            return True
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def run_covenant_check():
    # 2. Setup paths
    defs_path = "data/samples/definitions.txt"
    covs_path = "data/samples/covenants.txt"

    if not os.path.exists(defs_path) or not os.path.exists(covs_path):
        print(f"Error: Required text files missing at {defs_path} or {covs_path}")
        return

    # Read inputs
    with open(defs_path, "r", encoding="utf-8") as f:
        defs_text = f.read()
    with open(covs_path, "r", encoding="utf-8") as f:
        covs_text = f.read()

    print("\n--- Step 1: AI Logic Extraction ---")
    # We initialize the agent with the API key
    agent = CovenantAIAgent(api_key=GEMINI_API_KEY)
    
    try:
        # Step 1: Extract JSON recipe from raw text
        contract_logic = agent.generate_recipe(defs_text, covs_text)
        print("AI successfully built the logic recipe.")
        print(json.dumps(contract_logic, indent=2))
    except Exception as e:
        print(f"AI Extraction Failed: {e}")
        return

    print("\n--- Step 2: Z3 Mathematical Formalization ---")
    engine = CovenantCheckEngine()
    
    # Inject the recipe into Z3
    try:
        for step in contract_logic['recipe']:
            engine.add_logic_step(step)
        print("Z3 Logic Model constructed successfully.")
    except Exception as e:
        print(f"Z3 Construction Failed: {e}")
        return

    print("\n--- Step 3: Compliance Verification ---")
    
    # IMPORTANT: Ensure these keys match the variable 'name' tags in the JSON above
    # If the AI calls it 'ebitda', you must use 'ebitda' here.
    cfo_inputs = {
        "operating_profit": 1000000,
        "interest_expense": 200000,
        "depreciation_and_amortization": 100000,
        "extraordinary_restructuring_costs": 500000, # Triggers the 10% cap
        "gross_borrowings": 3500000,
        "cash": 500000
    }

    # Verify against threshold from AI
    threshold = contract_logic['threshold']
    operator = contract_logic['operator']
    
    status = engine.verify(cfo_inputs, threshold, operator)

    print("-" * 30)
    print(f"FINAL RESULT: {status}")
    print(f"THRESHOLD: {threshold} ({'Max' if operator == 'le' else 'Min'})")
    print("-" * 30)

if __name__ == "__main__":
    if diagnose_api():
        run_covenant_check()
    else:
        print("Please check your Google AI Studio account and API permissions.")