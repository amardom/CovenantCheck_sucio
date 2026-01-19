import json
from app.utils.report_pdf import generate_initial_report, generate_final_report
from app.core.z3_engine import verify_logics

FILENAME_INITIAL_REPORT = "report_initial.pdf" 
FILENAME_FINAL_REPORT = "report_final.pdf"

def main():

    # 1. Load json with vars and logics.
    with open("data/samples/NETFLIX/logics_NETFLIX.json", "r") as f:
        logics = json.load(f)

    # 2. Generate initial report from json.
    generate_initial_report(logics, FILENAME_INITIAL_REPORT)
    print(f"\nReport successfully generated in: {FILENAME_INITIAL_REPORT}\n")

    # 3. Read CFO data.
    cfo_data = json.load(open('data/samples/NETFLIX/cfo_data_NETFLIX.json'))

    # 4. Verify logics.
    res = verify_logics(logics, cfo_data)

    # 5. Generate final report from z3 results.
    generate_final_report(res, logics, cfo_data, FILENAME_FINAL_REPORT)
    print(f"\nReport successfully generated in: {FILENAME_FINAL_REPORT}\n")

if __name__ == "__main__":
    main()