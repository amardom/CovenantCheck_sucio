import json
from app.utils.report_pdf import generate_initial_report, generate_final_report
from app.core.z3_engine import validate_json, verify_logics
from app.core.deal import Deal

FILENAME_LOGICS = "logics_NETFLIX.json"
FILENAME_CFO_DATA = "cfo_data_NETFLIX.json"

FILENAME_INITIAL_REPORT = "report_initial" + "_" + FILENAME_LOGICS.removesuffix('.json') + ".pdf"
FILENAME_FINAL_REPORT = "report_final" + "_" + FILENAME_LOGICS.removesuffix('.json') + ".pdf"

def main():

    base_path = "data/samples/deal_"
    deal = Deal(1)
    deal.process_logics_and_cfodata(2026,"Q1", base_path)

    generate_initial_report(deal.history["2026"]["Q1"]["logics"], FILENAME_INITIAL_REPORT)
    print(f"\nReport successfully generated in: {FILENAME_INITIAL_REPORT}\n")

    generate_final_report(deal.history["2026"]["Q1"]["z3_result"], deal.history["2026"]["Q1"]["logics"], deal.history["2026"]["Q1"]["cfo_data"], FILENAME_FINAL_REPORT)
    print(f"\nReport successfully generated in: {FILENAME_FINAL_REPORT}\n")

if __name__ == "__main__":
    main()