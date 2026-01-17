import json
from app.utils.report_generator import generate_minimalist_report

def main():
    # 1. Cargar el JSON de lógica (el que validamos antes)
    with open("data/samples/var_logic.json", "r") as f:
        logic_data = json.load(f)

    # 2. Generar el PDF para el CFO
    output_pdf = "audit_report_CFO.pdf"
    generate_minimalist_report(logic_data, output_pdf)
    
    print(f"Reporte generado exitosamente en: {output_pdf}")

if __name__ == "__main__":
    main()