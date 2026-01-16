import os
import json
from dotenv import load_dotenv
# Make sure to install: pip install pymupdf
from app.utils.pdf_handler import PDFContractReader
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

# 1. Configuration & API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def run_pdf_covenant_check(pdf_path):
    if not GEMINI_API_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY not found in .env file.")
        return

    print(f"\nProcessing File: {pdf_path}")

    # 2. PDF Text Extraction
    # We convert the PDF into a string that the AI can read
    raw_text = PDFContractReader.extract_text(pdf_path)
    if not raw_text:
        print("Error: Could not extract text from PDF.")
        return

    # 3. AI Logic Extraction (Step 1)
    print("\n" + "="*50)
    print("STEP 1: AI EXTRACTION (DEBUG MODE)")
    print("="*50)
    
    agent = CovenantAIAgent(api_key=GEMINI_API_KEY)
    
    try:
        # We pass the same text to both fields since the PDF contains both
        contract_logic = agent.generate_recipe(defs_text=raw_text, covs_text=raw_text)
        
        # PRESERVING DEBUG OUTPUT: Printing the JSON recipe
        print("\n[AI JSON OUTPUT]:")
        print(json.dumps(contract_logic, indent=4))
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"AI Extraction Failed: {e}")
        return

    # 4. Z3 Formalization (Step 2)
    print("--- Step 2: Z3 Mathematical Formalization ---")
    engine = CovenantCheckEngine()
    
    try:
        for step in contract_logic['recipe']:
            engine.add_logic_step(step)
        print("Z3 Logic Model constructed successfully.")
    except Exception as e:
        print(f"Z3 Construction Failed: {e}")
        return

    # 5. CFO Input Data (Normalized Labels)
    cfo_inputs = {
        "bonds": 2000000,
        "bank_loans": 1500000,
        "cash_and_cash_equivalents": 500000,
        "operating_profit": 1000000,
        "interest_expense": 200000,
        "depreciation_and_amortization": 100000,
        "extraordinary_restructuring_costs": 500000 
    }

    # 6. Compliance Verification (Step 3)
    print("\n--- Step 3: Compliance Verification ---")
    threshold = contract_logic.get('threshold')
    operator = contract_logic.get('operator')
    
    # This will trigger the [Z3 Solver Proof] internally if it finds a BREACH
    status = engine.verify(cfo_inputs, threshold, operator)

    print("\n" + "#"*40)
    print(f"FINAL VERDICT: {status}")
    print(f"USING THRESHOLD: {threshold}")
    print(f"USING OPERATOR: {operator}")
    print("#"*40)

if __name__ == "__main__":
    # Ensure the path matches the filename you uploaded
    run_pdf_covenant_check("data/samples/loan_contract.pdf")