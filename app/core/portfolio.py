import json
from pathlib import Path
from app.utils.report_pdf import generate_initial_report, generate_final_report
from app.core.deal import Deal

FILENAME_LOGICS = "logics.json"
FILENAME_CFO_DATA = "cfo_data.json"

def create_portfolio(clients, years, quarters, root_path):

    assert isinstance(clients, list), "CLIENTS_NOT_A_LIST" 
    assert len(clients) > 0, "CLIENTS_LIST_EMPTY"
    assert all(isinstance(c, str) for c in clients), "CLIENT_NOT_A_STR"
    assert isinstance(years, list), "YEARS_NOT_A_LIST"
    assert len(years) > 0, "YEARS_LIST_EMPTY"
    assert all(int(years[i]) < int(years[i+1]) for i in range(len(years) - 1)), "YEARS_NOT_SORTED"
    assert all(isinstance(y, str) for y in years), "YEAR_NOT_A_STR"
    assert all(len(str(y)) == 4 for y in years), "YEAR_FORMAT_INVALID"
    assert isinstance(quarters, list), "QUARTERS_NOT_A_LIST"
    assert len(quarters) > 0, "QUARTERS_LIST_EMPTY"
    assert all(int(quarters[i][1]) < int(quarters[i+1][1]) for i in range(len(quarters)-1)), "QUARTERS_NOT_SORTED"
    assert all(isinstance(q, str) for q in quarters), "QUARTER_NOT_A_STR"
    assert all(q in ["Q1", "Q2", "Q3", "Q4"] for q in quarters), "QUARTER_FORMAT_INVALID"
    assert isinstance(root_path, str), "ROOT_PATH_NOT_A_STR"
    assert len(root_path) > 0, "ROOT_PATH_EMPTY"

    portfolio = {}

    for client_ID in clients:
        
        deal = Deal(client_ID)
        portfolio[client_ID] = deal

        for year in years:

            for quarter in quarters:
                
                year_quarter = f"{year}_{quarter}"

                print(f"\n-- Client: {client_ID} | {year_quarter} --")

                path = Path(f"{root_path}_{deal.id}/{year_quarter}")
                assert path.exists(), f"PATH_DOES_NOT_EXIST"

                path_logics = path / FILENAME_LOGICS
                assert path_logics.exists(), f"LOGICS_JSON_DOES_NOT_EXIST"
                with open(path_logics, "r") as f:
                    logics = json.load(f)

                path_cfo_data = path / FILENAME_CFO_DATA
                assert path_cfo_data.exists(), f"CFO_DATA_JSON_DOES_NOT_EXIST"
                with open(path_cfo_data, "r") as f:
                    cfo_data = json.load(f)

                deal.process_logics_and_cfo_data(year, quarter, logics, cfo_data)
                assert deal.history[year][quarter] is not None

                filename_initial_report = f"report_initial_{year_quarter}.pdf"
                filename_final_report = f"report_final_{year_quarter}.pdf"

                generate_initial_report(deal.history[year][quarter]["logics"], path / filename_initial_report)

                generate_final_report(deal.history[year][quarter]["z3_result"], deal.history[year][quarter]["logics"], 
                                      deal.history[year][quarter]["cfo_data"], path / filename_final_report)

    return portfolio