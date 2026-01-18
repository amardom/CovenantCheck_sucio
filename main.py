import json
from app.utils.report_generator import generate_minimalist_report
from app.core.z3_engine import verify_logics

def main():

    # 1. Load json with vars and logics.
    with open("data/samples/PDFSOLUTIONS/vars_and_logics_PDFSOLUTIONS.json", "r") as f:
        logic_data = json.load(f)

    # 2. Generate report from json.
    output_pdf = "audit_report_CFO.pdf"
    generate_minimalist_report(logic_data, output_pdf)
    print(f"\nReport successfully generated in: {output_pdf}\n")

    # 3. Read CFO data.
    cfo_data = json.load(open('data/samples/PDFSOLUTIONS/cfo_data_PDFSOLUTIONS.json'))

    # 4. Verify logics.
    verify_logics(logic_data, cfo_data)

if __name__ == "__main__":
    main()