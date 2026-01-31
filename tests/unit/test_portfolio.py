import json
from pathlib import Path
import pytest
from app.core.portfolio import create_portfolio

# --- CONSTANTES PARA TESTS ---
VALID_CLIENTS = ["Netflix"]
VALID_YEARS = ["2026"]
VALID_QUARTERS = ["Q1"]
VALID_PATH = "tests/scenarios/Fund_01/deal"

# --- 1. VALIDACIÓN DE INPUTS (La "Batería" de Asserts) ---

@pytest.mark.parametrize("c, y, q, path, expected_msg", [
    # Validación de Clientes
    ([], VALID_YEARS, VALID_QUARTERS, VALID_PATH, "CLIENTS_LIST_EMPTY"),
    ("string", VALID_YEARS, VALID_QUARTERS, VALID_PATH, "CLIENTS_NOT_A_LIST"),
    (123, VALID_YEARS, VALID_QUARTERS, VALID_PATH, "CLIENTS_NOT_A_LIST"),
    (None, VALID_YEARS, VALID_QUARTERS, VALID_PATH, "CLIENTS_NOT_A_LIST"),
    ([123], VALID_YEARS, VALID_QUARTERS, VALID_PATH, "CLIENT_NOT_A_STR"),
    
    # Validación de Años
    (VALID_CLIENTS, [], VALID_QUARTERS, VALID_PATH, "YEARS_LIST_EMPTY"),
    (VALID_CLIENTS, "string", VALID_QUARTERS, VALID_PATH, "YEARS_NOT_A_LIST"),
    (VALID_CLIENTS, 123, VALID_QUARTERS, VALID_PATH, "YEARS_NOT_A_LIST"),
    (VALID_CLIENTS, None, VALID_QUARTERS, VALID_PATH, "YEARS_NOT_A_LIST"),
    (VALID_CLIENTS, [123], VALID_QUARTERS, VALID_PATH, "YEAR_NOT_A_STR"),
    (VALID_CLIENTS, ["2026", "2025"], VALID_QUARTERS, VALID_PATH, "YEARS_NOT_SORTED"),
    
    # Validación de Trimestres
    (VALID_CLIENTS, VALID_YEARS, [], VALID_PATH, "QUARTERS_LIST_EMPTY"),
    (VALID_CLIENTS, VALID_YEARS, "string", VALID_PATH, "QUARTERS_NOT_A_LIST"),
    (VALID_CLIENTS, VALID_YEARS, 123, VALID_PATH, "QUARTERS_NOT_A_LIST"),
    (VALID_CLIENTS, VALID_YEARS, None, VALID_PATH, "QUARTERS_NOT_A_LIST"),
    (VALID_CLIENTS, VALID_YEARS, [123], VALID_PATH, "QUARTER_NOT_A_STR"),
    (VALID_CLIENTS, VALID_YEARS, ["Q5"], VALID_PATH, "QUARTER_FORMAT_INVALID"),
    (VALID_CLIENTS, VALID_YEARS, ["Q4", "Q3"], VALID_PATH, "QUARTERS_NOT_SORTED"),
    
    # Validación de Path (Root Path)
    (VALID_CLIENTS, VALID_YEARS, VALID_QUARTERS, [], "ROOT_PATH_NOT_A_STR"),
    (VALID_CLIENTS, VALID_YEARS, VALID_QUARTERS, 123, "ROOT_PATH_NOT_A_STR"),
    (VALID_CLIENTS, VALID_YEARS, VALID_QUARTERS, None, "ROOT_PATH_NOT_A_STR"),
    (VALID_CLIENTS, VALID_YEARS, VALID_QUARTERS, "", "ROOT_PATH_EMPTY"),
    (VALID_CLIENTS, VALID_YEARS, VALID_QUARTERS, "tests/scenarios/deal_bad", "PATH_DOES_NOT_EXIST"),
])
def test_create_portfolio_assertions(c, y, q, path, expected_msg):
    with pytest.raises(AssertionError) as exc:
        create_portfolio(c, y, q, path)
    assert str(exc.value) == expected_msg

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

    logics = {"audit_id": f"{client_id}_{year_quarter}.json"}
    (period_folder / "logics.json").write_text(json.dumps(logics))

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

    clients = ["companyHealth", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/Fund_01")

    assert len(portfolio) == 2
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