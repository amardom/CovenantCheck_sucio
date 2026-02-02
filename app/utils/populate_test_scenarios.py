import json
from pathlib import Path

def populate_company():
    client_id = "TechGrowth"
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    base_path = Path(f"tests/scenarios/Fund_02/{client_id}")
    
    # Valores iniciales coherentes
    revenue_base = 800000.0
    total_debt_base = 1200000.0
    cash_base = 250000.0
    min_ebitda_req = 120000.0  # El suelo del contrato

    for year in years:
        for q in quarters:
            q_idx = (int(year) - 2024) * 4 + quarters.index(q)
            
            # Simulamos el deterioro real
            current_rev = revenue_base * (1.02 ** q_idx) # Crece poco a poco
            # El ratio de gastos sube: del 70% al 86% (en Q8 será insostenible)
            current_opex = current_rev * (0.70 + (q_idx * 0.02)) 
            current_debt = total_debt_base + (q_idx * 20000.0)
            current_cash = max(cash_base - (q_idx * 30000.0), 10000.0)

            logics_content = {
                "audit_id": f"{client_id}_{year}_{q}",
                "contract_name": "Senior Secured Credit Agreement",
                "variables": [
                    {"name": "revenue", "definition": "Net Sales", "definition_page": 4},
                    {"name": "operating_expenses", "definition": "SG&A", "definition_page": 5},
                    {"name": "ebitda", "definition": "Consolidated EBITDA", "definition_page": 6},
                    {"name": "total_debt", "definition": "Total Indebtedness", "definition_page": 9},
                    {"name": "cash", "definition": "Unrestricted Cash", "definition_page": 12},
                    {"name": "net_debt", "definition": "Total Debt - Cash", "definition_page": 9},
                    {"name": "leverage_ratio", "definition": "Net Leverage", "definition_page": 18},
                    {"name": "min_ebitda_threshold", "definition": "Covenant Floor", "definition_page": 45}
                ],
                "logical_conditions": [
                    {"id": 1, "formula": "ebitda == revenue - operating_expenses", "evidence": "Def. EBITDA", "evidence_page": 6},
                    {"id": 2, "formula": "net_debt == total_debt - cash", "evidence": "Def. Net Debt", "evidence_page": 9},
                    {"id": 3, "formula": "leverage_ratio == net_debt / ebitda", "evidence": "Ratio Calc", "evidence_page": 18},
                    {"id": 4, "formula": "leverage_ratio <= 4.5", "evidence": "Max Leverage", "evidence_page": 44},
                    {"id": 5, "formula": "ebitda >= min_ebitda_threshold", "evidence": "Min EBITDA", "evidence_page": 45}
                ]
            }

            cfo_content = {
                "revenue": round(current_rev, 2),
                "operating_expenses": round(current_opex, 2),
                "total_debt": round(current_debt, 2),
                "cash": round(current_cash, 2),
                "min_ebitda_threshold": min_ebitda_req
            }

            folder = base_path / f"{year}_{q}"
            folder.mkdir(parents=True, exist_ok=True)

            with open(folder / "logics.json", "w") as f:
                json.dump(logics_content, f, indent=4)
            with open(folder / "cfo_data.json", "w") as f:
                json.dump(cfo_content, f, indent=4)

    print(f"✅ Escenario '{client_id}' poblado con sistema cerrado.")

if __name__ == "__main__":
    populate_company()