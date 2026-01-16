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
        print("ERROR: GEMINI_API_KEY no configurada.")
        return

    reader = PDFContractReader()
    agent = CovenantAIAgent(api_key=GEMINI_API_KEY)
    engine = CovenantCheckEngine()

    # --- STEP 0: NAVIGATION ---
    print(f"--- Step 0: Navigating PDF Structure ---")
    skeleton = reader.get_skeleton(pdf_path) # Asegúrate que lea suficientes caracteres
    nav_map = agent.identify_sections(skeleton)
    
    # Unimos las páginas encontradas eliminando duplicados
    target_pages = list(set(nav_map.get('definitions_pages', [1]) + nav_map.get('covenants_pages', [1])))
    print(f"[DEBUG] Navigator found pages: {nav_map}")
    
    clean_text = reader.extract_specific_pages(pdf_path, target_pages)

    # --- STEP 1: AI LOGIC EXTRACTION ---
    print("\n" + "="*50)
    print("STEP 1: AI EXTRACTION (ARCHITECT PASS)")
    print("="*50)
    
    try:
        contract_logic = agent.generate_recipe(clean_text)
        print("\n[AI JSON OUTPUT]:")
        print(json.dumps(contract_logic, indent=4))
    except Exception as e:
        print(f"Fallo en la extracción: {e}")
        return

    # --- STEP 2: Z3 FORMALIZATION ---
    print("\n--- Step 2: Z3 Logic Construction ---")
    for step in contract_logic['recipe']:
        engine.add_logic_step(step)

    # --- STEP 3: VERIFICATION ---
    cfo_inputs = {
        "borrowings": 3500000, # (2M de bonds + 1.5M de loans)
        "cash_and_cash_equivalents": 500000,
        "operating_profit": 1000000, 
        "interest_expense": 200000,
        "depreciation_and_amortization": 100000, 
        "extraordinary_restructuring_costs": 130000 # (Cap del 10% ya calculado)
    }

    print("\n--- Step 3: Compliance Verification ---")
    status = engine.verify(cfo_inputs, contract_logic['threshold'], contract_logic['operator'])

    print("\n" + "#"*40)
    print(f"RESULTADO FINAL: {status}")
    print(f"UMBRAL: {contract_logic['threshold']} | OP: {contract_logic['operator']}")
    print("#"*40)

if __name__ == "__main__":
    run_production_check("data/samples/loan_contract.pdf")