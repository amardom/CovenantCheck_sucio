import os
import json
from dotenv import load_dotenv
from app.utils.pdf_handler import PDFContractReader
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def run_production_check(pdf_path):
    if not GEMINI_API_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY not found.")
        return

    reader = PDFContractReader()
    agent = CovenantAIAgent(api_key=GEMINI_API_KEY)

    # --- STEP 0: NAVIGATION ---
    print(f"--- Step 0: Navigating PDF Structure ---")
    skeleton = reader.get_skeleton(pdf_path)
    
    try:
        #nav_map = agent.identify_sections(skeleton)
        nav_map = {'definitions_pages': [1], 'covenants_pages': [1]}
        print(f"[DEBUG] Navigator found pages: {nav_map}")
        
        # Merge detected pages
        target_pages = list(set(nav_map['definitions_pages'] + nav_map['covenants_pages']))
        clean_text = reader.extract_specific_pages(pdf_path, target_pages)
    except Exception as e:
        print(f"Navigation Pass Failed: {e}")
        return

    # --- STEP 1: AI LOGIC EXTRACTION ---
    print("\n" + "="*50)
    print("STEP 1: AI EXTRACTION (DEBUG MODE)")
    print("="*50)
    
    try:
        contract_logic = agent.generate_recipe(clean_text)
        print("\n[AI JSON OUTPUT]:")
        print(json.dumps(contract_logic, indent=4))
        print("="*50)
    except Exception as e:
        print(f"Architect Pass Failed: {e}")
        return

    # --- STEP 2: Z3 FORMALIZATION ---
    print("\n--- Step 2: Z3 Mathematical Formalization ---")
    engine = CovenantCheckEngine()
    for step in contract_logic['recipe']:
        engine.add_logic_step(step)
    print("Z3 Logic Model constructed successfully.")

    # --- STEP 3: COMPLIANCE VERIFICATION ---
    cfo_inputs = {
        "bonds": 2000000, "bank_loans": 1500000, "cash_and_cash_equivalents": 500000,
        "operating_profit": 1000000, "interest_expense": 200000,
        "depreciation_and_amortization": 100000, "extraordinary_restructuring_costs": 500000 
    }

    print("\n--- Step 3: Compliance Verification ---")
    status = engine.verify(cfo_inputs, contract_logic['threshold'], contract_logic['operator'])

    print("\n" + "#"*40)
    print(f"FINAL VERDICT: {status}")
    print(f"USING THRESHOLD: {contract_logic['threshold']} | OPERATOR: {contract_logic['operator']}")
    print("#"*40)

if __name__ == "__main__":
    # Ensure this path is correct for your local setup
    run_production_check("data/samples/loan_contract.pdf")