import pytest
from app.core.deal import Deal

def test_deal_flow():

    client_id = "CompanyTech_2026"
    deal = Deal(client_id)

    logics_mock = {
        "source_file": "logics.json",
        "contract_name": "Credit Agreement - NETFLIX, INC. (2009)",
        "variables": [
            {"name": "consolidated_ebitda", "definition": "Calculated EBITDA"},
            {"name": "consolidated_net_debt", "definition": "Total debt minus cash"},
            {"name": "consolidated_leverage_ratio", "definition": "Leverage Ratio"}
        ],
        "logical_conditions": [
            {
                "id": 1,
                "formula": "consolidated_leverage_ratio == consolidated_net_debt / consolidated_ebitda",
                "evidence": "Section 1.01"
            },
            {
                "id": 2,
                "formula": "consolidated_leverage_ratio <= 2.5",
                "evidence": "Section 7.12"
            }
        ]
    }

    cfo_data_mock = {
        "consolidated_ebitda": 2000000,
        "consolidated_net_debt": 4000000
    }

    year = "2026"
    quarter = "Q1"
    deal.process_logics_and_cfo_data(year, quarter, logics_mock, cfo_data_mock)

    assert deal.id == client_id
    assert year in deal.history

    entry = deal.history[year][quarter]
    assert len(entry["cfo_data"]) == 2
    assert entry["cfo_data"]["consolidated_ebitda"] == 2000000
    assert entry["logics"]["variables"][1]["name"] == "consolidated_net_debt"
    assert entry["logics"]["logical_conditions"][1]["formula"] == "consolidated_leverage_ratio <= 2.5"
    assert entry["z3_result"]["is_compliant"] == True

def test_deal_year_and_quarter():

    client_id = "CompanyTech_2026"
    deal = Deal(client_id)

    with pytest.raises(AssertionError):
        deal.process_logics_and_cfo_data(2026, "Q1", {}, {})

    with pytest.raises(AssertionError):
        deal.process_logics_and_cfo_data("2026", "Q5", {}, {})