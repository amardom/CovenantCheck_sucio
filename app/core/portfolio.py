import json
from pathlib import Path
from app.utils.report_pdf import generate_initial_report, generate_final_report
from app.core.z3_engine import validate_json
from app.core.deal import Deal

FILENAME_LOGICS = "logics.json"
FILENAME_CFO_DATA = "cfo_data.json"

FILENAME_INITIAL_REPORT = "report_initial" + "_" + FILENAME_LOGICS.removesuffix('.json') + ".pdf"
FILENAME_FINAL_REPORT = "report_final" + "_" + FILENAME_LOGICS.removesuffix('.json') + ".pdf"

def create_portfolio(clients, years, quarters):

    assert isinstance(clients, list) and len(clients) > 0
    assert isinstance(years, list) and len(years) > 0
    assert isinstance(quarters, list) and len(quarters) > 0
    assert all(isinstance(c, str) for c in clients)
    assert all(isinstance(y, str) for y in years)
    assert all(q in ["Q1", "Q2", "Q3", "Q4"] for q in quarters)

    portfolio = {}

    for client_ID in clients:
        
        deal = Deal(client_ID)
        portfolio[client_ID] = deal

        for year in years:

            for quarter in quarters:
                
                print(f"\n-- Client: {client_ID} | {year}_{quarter} --")

                path = Path(f"tests/scenarios/deal_{deal.id}/{str(year)}_{quarter}")
                assert path.exists()

                with open(path / FILENAME_LOGICS, "r") as f:
                    logics = json.load(f)
                validate_json(FILENAME_LOGICS, logics)

                with open(path / FILENAME_CFO_DATA, "r") as f:
                    cfo_data = json.load(f)

                deal.process_logics_and_cfo_data(year, quarter, logics, cfo_data)
                assert deal.history[year][quarter] is not None

                generate_initial_report(deal.history[year][quarter]["logics"], path / FILENAME_INITIAL_REPORT)

                generate_final_report(deal.history[year][quarter]["z3_result"], deal.history[year][quarter]["logics"], 
                                      deal.history[year][quarter]["cfo_data"], path / FILENAME_FINAL_REPORT)

    return portfolio