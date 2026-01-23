import json
from pathlib import Path

def populate_company():
    client_id = "companyHealth"
    years = ["2025", "2026"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    
    logics_content = {
        "source_file": "logics.json",
        "contract_name": "HealthCorp Strategic Credit Facilities",
        "variables": [
            {"name": "revenue", "definition": "Total Operating Revenue", "definition_page": 5},
            {"name": "operating_expenses", "definition": "Total Operating Expenses", "definition_page": 5},
            {"name": "ebitda", "definition": "Consolidated EBITDA", "definition_page": 6},
            {"name": "total_debt", "definition": "Total Indebtedness", "definition_page": 8},
            {"name": "cash", "definition": "Unrestricted Cash", "definition_page": 12},
            {"name": "net_debt", "definition": "Consolidated Net Debt", "definition_page": 8},
            {"name": "leverage_ratio", "definition": "Consolidated Leverage Ratio", "definition_page": 15}
        ],
        "logical_conditions": [
            {
                "id": 1, 
                "formula": "ebitda == revenue - operating_expenses", 
                "evidence": "Definition of EBITDA (Section 1.01)", 
                "evidence_page": 6
            },
            {
                "id": 2, 
                "formula": "net_debt == total_debt - cash", 
                "evidence": "Net Debt Calculation (Section 1.01)", 
                "evidence_page": 8
            },
            {
                "id": 3, 
                "formula": "leverage_ratio == net_debt / ebitda", 
                "evidence": "Ratio Calculation Methodology", 
                "evidence_page": 15
            },
            {
                "id": 4, 
                "formula": "leverage_ratio <= 3.0", 
                "evidence": "Maximum Leverage Ratio (Section 7.12)", 
                "evidence_page": 42
            }
        ]
    }

    # 2. Ruta destino (dentro de tests/scenarios como pediste)
    base_path = Path(f"tests/scenarios/deal_{client_id}")
    
    for year in years:
        for q in quarters:
            folder = base_path / f"{year}_{q}"
            folder.mkdir(parents=True, exist_ok=True)

            # Datos CFO consistentes
            # 2024 Q1: EBITDA 150k, NetDebt 300k -> Ratio 2.0 (PASS)
            # Vamos subiendo el gasto para estresar el ratio
            q_index = quarters.index(q)
            cfo_content = {
                "revenue": 500000,
                "operating_expenses": 350000 + (q_index * 10000), # Sube el gasto
                "total_debt": 400000,
                "cash": 100000 - (q_index * 5000) # Baja el cash
            }

            with open(folder / "logics.json", "w") as f:
                json.dump(logics_content, f, indent=4)
            
            with open(folder / "cfo_data.json", "w") as f:
                json.dump(cfo_content, f, indent=4)

    print(f"✅ Escenario '{client_id}' populado con metadatos completos en {base_path}")

if __name__ == "__main__":
    populate_company()