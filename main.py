import json
from app.utils.report_generator import generate_minimalist_report
from app.core.z3_engine import auditor_z3_pro

def main():
    # 1. Cargar el JSON de lógica (el que validamos antes)
    with open("data/samples/var_logic.json", "r") as f:
        logic_data = json.load(f)

    # 2. Generar el PDF para el CFO
    output_pdf = "audit_report_CFO.pdf"
    generate_minimalist_report(logic_data, output_pdf)
    
    print(f"Reporte generado exitosamente en: {output_pdf}")

    cfo_data = {
    "consolidated_net_income": 5000000,
    "interest_expense": 1000000,
    "tax_expense": 1200000,
    "depreciation_amortization": 800000,
    "restructuring_costs": 1500000,
    "capped_ebitda_add_backs": 1500000,
    "consolidated_funded_indebtedness": 12000000,
    "unrestricted_cash": 2000000,
    "purchase_money_indebtedness": 500000,
    "consolidated_ttm_ebitda": 9500000
    }

    auditor_z3_pro(logic_data, cfo_data)

if __name__ == "__main__":
    main()