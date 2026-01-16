import os
import json
from dotenv import load_dotenv
from app.core.ai_agent import CovenantAIAgent
from app.core.z3_engine import CovenantCheckEngine

load_dotenv()

def clean_key(key: str) -> str:
    return key.lower().replace(" ", "_").replace("-", "_")

def run_covenant_check():
    agent = CovenantAIAgent(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Load your files from data/samples/
    with open("data/samples/definitions.txt", "r") as f: defs = f.read()
    with open("data/samples/covenants.txt", "r") as f: covs = f.read()

    # 1. AI Extraction
    contract_logic = agent.generate_recipe(defs, covs)
    
    # 2. Z3 Setup
    engine = CovenantCheckEngine()
    for step in contract_logic['recipe']:
        engine.add_logic_step(step)

    # 3. CFO Inputs - Standardized keys
    raw_inputs = {
        "Operating Profit Before Taxation": 1000000,
        "Interest Expense": 200000,
        "Depreciation and Amortization": 100000,
        "Extraordinary Restructuring Costs": 500000,
        "Bonds": 2000000,
        "Bank Loans": 1500000,
        "Cash and Cash Equivalents": 500000
    }
    cfo_inputs = {clean_key(k): v for k, v in raw_inputs.items()}

    # 4. Verify
    result = engine.verify(cfo_inputs, contract_logic['threshold'], contract_logic['operator'])
    
    print(f"Final Result: {result}")
    print(f"Formula used by AI: {json.dumps(contract_logic['recipe'], indent=2)}")

if __name__ == "__main__":
    run_covenant_check()