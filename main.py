import json
from app.utils.report_generator import generate_minimalist_report
from app.core.z3_engine import auditor_z3_pro

def main():
    # 1. Cargar el JSON de lógica (el que validamos antes)
    with open("data/samples/PDFSOLUTIONS/vars_and_logics_PDFSOLUTIONS.json", "r") as f:
        logic_data = json.load(f)

    # 2. Generar el PDF para el CFO
    output_pdf = "audit_report_CFO.pdf"
    generate_minimalist_report(logic_data, output_pdf)
    
    print(f"Reporte generado exitosamente en: {output_pdf}")

    # 3. Leemos datos del CFO.
    cfo_data = json.load(open('data/samples/PDFSOLUTIONS/cfo_data_PDFSOLUTIONS.json'))

    auditor_z3_pro(logic_data, cfo_data)

if __name__ == "__main__":
    main()