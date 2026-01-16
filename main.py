import os
import json
from dotenv import load_dotenv
from app.utils.pdf_handler import PDFContractReader
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

def main():
    # 0. Load Configuration
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found in .env file")
        return

    # 1. Initialize Components
    pdf_path = "data/samples/loan_contract.pdf"
    reader = PDFContractReader(pdf_path)
    agent = CovenantAIAgent(api_key)
    engine = CovenantCheckEngine()

    print(f"--- Starting analysis for: {pdf_path} ---")

    # 2. PDF Navigation & Extraction
    # Step 0: Get the skeleton to locate relevant pages
    skeleton = reader.get_skeleton()
    nav_data = agent.identify_sections(skeleton)
    
    # Select pages for Definitions and Covenants
    target_pages = list(set(nav_data.get("definitions_pages", [1]) + nav_data.get("covenants_pages", [1])))
    clean_text = reader.extract_pages(target_pages)

    # 3. AI Pass: Parameter Extraction (Architect)
    print("\n" + "="*50)
    print("STEP 1: AI PARAMETER EXTRACTION")
    print("="*50)
    
    try:
        # Extracting flat parameters and dynamic caps (like the 10%)
        contract_params = agent.generate_recipe(clean_text)
        print("[AI JSON OUTPUT]:")
        print(json.dumps(contract_params, indent=4))
    except Exception as e:
        print(f"[CRITICAL ERROR] AI Extraction failed: {e}")
        return

    # 4. Z3 Pass: Logic Construction
    print("\n" + "="*50)
    print("STEP 2: Z3 LOGIC CONSTRUCTION")
    print("="*50)
    
    # We inject the logic parameters into the formal solver
    engine.add_logic(contract_params)
    print("[LOG] Mathematical logic injected into Z3 Solver.")

    # 5. Compliance Verification: CFO Inputs
    print("\n" + "="*50)
    print("STEP 3: COMPLIANCE VERIFICATION")
    print("="*50)

    # Scenario: 5M in Bonds to test the BREACH condition
    cfo_inputs = {
        "bonds": 1000000,
        "bank_loans": 1500000,
        "cash_and_cash_equivalents": 500000,
        "operating_profit": 1000000,
        "interest_expense": 200000,
        "depreciation_and_amortization": 100000,
        "extraordinary_restructuring_costs": 500000  # Z3 will apply the 10% cap here
    }

    print(f"[CFO INPUTS]: {json.dumps(cfo_inputs, indent=2)}")

    # Final Verification
    status = engine.verify(
        inputs=cfo_inputs, 
        threshold=contract_params['threshold'], 
        operator=contract_params['operator']
    )

    # 6. Final Result Display
    print("\n" + "#" * 40)
    print(f"FINAL RESULT: {status}")
    print(f"THRESHOLD: {contract_params['threshold']} | OPERATOR: {contract_params['operator']}")
    print("#" * 40 + "\n")

if __name__ == "__main__":
    main()