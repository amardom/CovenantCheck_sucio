import json
from app.utils.report_generator import generate_minimalist_report
from app.core.z3_engine import verify_logics
from app.utils.report_final import create_audit_pdf

def main():

    # 1. Load json with vars and logics.
    with open("data/samples/NETFLIX/vars_and_logics_NETFLIX.json", "r") as f:
        logic_data = json.load(f)

    # 2. Generate initial report from json.
    output_pdf = "report_initial.pdf"
    generate_minimalist_report(logic_data, output_pdf)
    print(f"\nReport successfully generated in: {output_pdf}\n")

    # 3. Read CFO data.
    cfo_data = json.load(open('data/samples/NETFLIX/cfo_data_NETFLIX.json'))

    # 4. Verify logics.
    res = verify_logics(logic_data, cfo_data)

    # 5. Generate final report from z3 results.
    output_pdf = "report_final.pdf"
    create_audit_pdf(res, "CONTRASTO--", cfo_data, output_pdf)
    print(f"\nReport successfully generated in: {output_pdf}\n")

if __name__ == "__main__":
    main()