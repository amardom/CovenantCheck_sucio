import json
from app.utils.integrity_json import validate_json
from app.utils.report_pdf import generate_initial_report, generate_final_report
from app.core.z3_engine import verify_logics

FILENAME_LOGICS = "logics_NETFLIX.json"
FILENAME_CFO_DATA = "cfo_data_NETFLIX.json"

FILENAME_INITIAL_REPORT = "report_initial.pdf" 
FILENAME_FINAL_REPORT = "report_final.pdf"

def main():

    # 1. Load json with vars and logics.
    with open("data/samples/NETFLIX/" + FILENAME_LOGICS, "r") as f:
        logics = json.load(f)
    validate_json(FILENAME_LOGICS, logics)

    # 2. Generate initial report from json.
    generate_initial_report(logics, FILENAME_INITIAL_REPORT)
    print(f"\nReport successfully generated in: {FILENAME_INITIAL_REPORT}\n")

    # 3. Read CFO data.
    with open("data/samples/NETFLIX/" + FILENAME_CFO_DATA, "r") as f:
        cfo_data = json.load(f)

    # 4. Verify logics.
    z3_result = verify_logics(logics, cfo_data)

    # 5. Generate final report from z3 results.
    generate_final_report(z3_result, logics, cfo_data, FILENAME_FINAL_REPORT)
    print(f"\nReport successfully generated in: {FILENAME_FINAL_REPORT}\n")

if __name__ == "__main__":
    main()