import json
from pathlib import Path
from app.utils.report_pdf import generate_initial_report, generate_final_report
from app.core.z3_engine import validate_json
from app.core.deal import Deal

FILENAME_LOGICS = "logics.json"
FILENAME_CFO_DATA = "cfo_data.json"

FILENAME_INITIAL_REPORT = "report_initial" + "_" + FILENAME_LOGICS.removesuffix('.json') + ".pdf"
FILENAME_FINAL_REPORT = "report_final" + "_" + FILENAME_LOGICS.removesuffix('.json') + ".pdf"

def process_portfolio(clients, years, quarters):

    portfolio = {}

    for client_ID in clients:
        
        deal = Deal(client_ID)
        portfolio[client_ID] = deal

        for year in years:

            for quarter in quarters:

                path = Path(f"data/samples/deal_{deal.id}/{str(year)}_{quarter}")

                with open(path / FILENAME_LOGICS, "r") as f:
                    logics = json.load(f)
                validate_json(FILENAME_LOGICS, logics)

                with open(path / FILENAME_CFO_DATA, "r") as f:
                    cfo_data = json.load(f)

                deal.process_logics_and_cfo_data(year, quarter, logics, cfo_data)

                generate_initial_report(deal.history[year][quarter]["logics"], path / FILENAME_INITIAL_REPORT)
                print(f"\nReport successfully generated in: {FILENAME_INITIAL_REPORT}\n")

                generate_final_report(deal.history[year][quarter]["z3_result"], deal.history[year][quarter]["logics"], 
                                      deal.history[year][quarter]["cfo_data"], path / FILENAME_FINAL_REPORT)
                print(f"\nReport successfully generated in: {FILENAME_FINAL_REPORT}\n")

    return portfolio