import json
from pathlib import Path
import pytest
from app.core.portfolio import create_portfolio

def test_portfolio_inputs():
    print("")
    invalid_inputs = [([], "CLIENTS_LIST_EMPTY"),
                    ("a string", "CLIENTS_NOT_A_LIST"),
                    (123, "CLIENTS_NOT_A_LIST"),
                    (None, "CLIENTS_NOT_A_LIST"),
                    ([123], "CLIENT_NOT_A_STR")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            create_portfolio(invalid, ["2026"], ["Q1"], "tests/scenarios/Fund_01/deal")
        assert str(exc.value) == expected_msg
        print(f"ERROR: {exc.value}")

    invalid_inputs = [([], "YEARS_LIST_EMPTY"),
                    ("a string", "YEARS_NOT_A_LIST"),
                    (123, "YEARS_NOT_A_LIST"),
                    (None, "YEARS_NOT_A_LIST"),
                    ([123], "YEAR_NOT_A_STR")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            create_portfolio(["Netflix"], invalid, ["Q1"], "tests/scenarios/Fund_01/deal")
        assert str(exc.value) == expected_msg
        print(f"ERROR: {exc.value}")

    invalid_inputs = [([], "QUARTERS_LIST_EMPTY"),
                    ("a string", "QUARTERS_NOT_A_LIST"),
                    (123, "QUARTERS_NOT_A_LIST"),
                    (None, "QUARTERS_NOT_A_LIST"),
                    ([123], "QUARTER_NOT_A_STR"),
                    (["Q5"], "QUARTER_FORMAT_INVALID")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            create_portfolio(["Netflix"], ["2026"], invalid, "tests/scenarios/Fund_01/deal")
        assert str(exc.value) == expected_msg
        print(f"ERROR: {exc.value}")
    
    invalid_inputs = [([], "ROOT_PATH_NOT_A_STR"),
                    (123, "ROOT_PATH_NOT_A_STR"),
                    (None, "ROOT_PATH_NOT_A_STR"),
                    (str(), "ROOT_PATH_EMPTY")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            create_portfolio(["Netflix"], ["2026"], ["Q4"], invalid)
        assert str(exc.value) == expected_msg
        print(f"ERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026", "2025"], ["Q4"], "tests/scenarios/Fund_01/deal")
    assert str(exc.value) == "YEARS_NOT_SORTED"
    print(f"ERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], ["Q4", "Q3"], "tests/scenarios/Fund_01/deal")
    assert str(exc.value) == "QUARTERS_NOT_SORTED"
    print(f"ERROR: {exc.value}")

def test_portfolio_path():

    bad_path = "tests/scenarios/deal_bad"
    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], ["Q1"], bad_path)
    assert str(exc.value) == "PATH_DOES_NOT_EXIST"
    print(f"ERROR: {exc.value}")

def test_portfolio_logics_json_exist(tmp_path):
    client_id = "Client1"
    year_quarter = "2026_Q1"
    
    client_folder = tmp_path / f"{client_id}"
    period_folder = client_folder / year_quarter
    period_folder.mkdir(parents=True)

    with pytest.raises(AssertionError) as exc:
        create_portfolio(
            clients=[client_id], 
            years=["2026"], 
            quarters=["Q1"], 
            root_path=str(tmp_path)
        )
    assert str(exc.value) == "LOGICS_JSON_DOES_NOT_EXIST"
    print(f"ERROR: {exc.value}")

def test_portfolio_cfo_data_json_exist(tmp_path):
    client_id = "Client1"
    year_quarter = "2026_Q1"
    
    client_folder = tmp_path / f"{client_id}"
    period_folder = client_folder / year_quarter
    period_folder.mkdir(parents=True)

    (period_folder / "logics.json").write_text("{}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(
            clients=[client_id], 
            years=["2026"], 
            quarters=["Q1"], 
            root_path=str(tmp_path)
        )
    assert str(exc.value) == "CFO_DATA_JSON_DOES_NOT_EXIST"
    print(f"ERROR: {exc.value}")

def test_portfolio_indexing():

    clients = ["companyHealth", "companyRealEstate", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/Fund_01")

    assert len(portfolio) == 3
    assert set(portfolio.keys()) == set(clients)

    for client_id in clients:
        deal = portfolio[client_id]
        
        assert len(deal.history) == len(years)
        
        for year in years:
            assert year in deal.history
            
            for q in quarters:
                
                entry = deal.history[year][q]
                assert entry is not None
                
                expected_contract = f"{client_id} Strategic Credit Facilities"
                assert entry["logics"]["contract_name"] == expected_contract
                assert len(entry["cfo_data"]) > 0
                assert isinstance(entry["cfo_data"]["revenue"], (int, float))
                assert "is_compliant" in entry["z3_result"]
                assert isinstance(entry["z3_result"]["is_compliant"], bool)
                assert "definition" in entry["logics"]["variables"][0]