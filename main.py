import os
import json
from dotenv import load_dotenv
from app.utils.pdf_handler import PDFContractReader
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    # El contrato de 300 páginas (PDF Solutions 001)
    pdf_path = "data/samples/loan_contract_001.pdf" 
    
    reader = PDFContractReader(pdf_path)
    agent = CovenantAIAgent(api_key)
    engine = CovenantCheckEngine()

    print(f"--- Processing Large Contract: {pdf_path} ---")

    # 1. Búsqueda semántica de cláusulas (Genérico)
    print("STEP 0: Searching for relevant clauses...")
    clean_text = reader.extract_relevant_context(["Consolidated EBITDA", "Leverage Ratio", "Indebtedness"])

    # 2. IA extrae la "Receta" (Mapping Dinámico)
    print("STEP 1: Extracting logic with Dynamic Mapping...")
    try:
        contract_params = agent.generate_recipe(clean_text)
        print("[AI JSON OUTPUT]:")
        print(json.dumps(contract_params, indent=4))
    except Exception as e:
        print(f"AI Error: {e}")
        return

    # 3. Z3 construye las fórmulas
    print("STEP 2: Building Z3 Logic...")
    engine.add_logic(contract_params)

    # 4. Datos del CFO Hardcoded (Para probar el contrato 001)
    # Supongamos estos números para PDF Solutions Inc.
    cfo_inputs = {
        "bank_loans": 35000000,           # $35M de deuda bancaria
        "cash_and_cash_equivalents": 8000000,  # $8M en caja
        "operating_profit": 10000000,      # $10M beneficio
        "interest_expense": 1200000,
        "depreciation_and_amortization": 1800000,
        "extraordinary_restructuring_costs": 4000000 # Coste alto para probar el CAP
    }

    print(f"\n[CFO INPUTS]: {json.dumps(cfo_inputs, indent=2)}")

    # 5. Verificación Final
    status = engine.verify(
        inputs=cfo_inputs, 
        threshold=contract_params['threshold'], 
        operator=contract_params['operator']
    )

    print("\n" + "#" * 40)
    print(f"FINAL COMPLIANCE STATUS: {status}")
    print("#" * 40 + "\n")

if __name__ == "__main__":
    main()