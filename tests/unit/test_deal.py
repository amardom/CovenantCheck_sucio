import pytest
from app.core.deal import Deal

def test_deal_flow():

    client_id = "CompanyTech"
    deal = Deal(client_id)

    year = "2026"
    quarter = "Q1"

    logics_mock = {
        "audit_id": f"{client_id}_{year}_{quarter}",
        "contract_name": "Credit Agreement - NETFLIX, INC. (2009)",
        "variables": [
            {"name": "consolidated_ebitda", "definition": "Calculated EBITDA", "definition_page": 9},
            {"name": "consolidated_net_debt", "definition": "Total debt minus cash", "definition_page": 19},
            {"name": "consolidated_leverage_ratio", "definition": "Leverage Ratio", "definition_page": 29}
        ],
        "logical_conditions": [
            {
                "id": 1,
                "formula": "consolidated_leverage_ratio == consolidated_net_debt / consolidated_ebitda",
                "evidence": "Section 1.01",
                "evidence_page": 10
            },
            {
                "id": 2,
                "formula": "consolidated_leverage_ratio <= 2.5",
                "evidence": "Section 7.12",
                "evidence_page": 11
            }
        ]
    }

    cfo_data_mock = {
        "consolidated_ebitda": 2000000,
        "consolidated_net_debt": 4000000
    }

    deal.process_logics_and_cfo_data(year, quarter, logics_mock, cfo_data_mock)

    assert deal.id == client_id
    assert year in deal.history

    entry = deal.history[year][quarter]
    assert len(entry["cfo_data"]) == 2
    assert entry["cfo_data"]["consolidated_ebitda"] == 2000000
    assert entry["logics"]["variables"][1]["name"] == "consolidated_net_debt"
    assert entry["logics"]["logical_conditions"][1]["formula"] == "consolidated_leverage_ratio <= 2.5"
    assert entry["z3_result"]["is_compliant"] == True

@pytest.mark.parametrize("invalid_year, expected_msg", [
    ([], "YEAR_NOT_STR"),
    (123, "YEAR_NOT_STR"),
    (None, "YEAR_NOT_STR"),
    ("26", "YEAR_FORMAT_INVALID"),
    ("20265", "YEAR_FORMAT_INVALID"),
])
def test_deal_year_validation(invalid_year, expected_msg):
    deal = Deal("CompanyTech")
    with pytest.raises(AssertionError) as exc:
        deal.process_logics_and_cfo_data(invalid_year, "Q1", {}, {})
    assert str(exc.value) == expected_msg

@pytest.mark.parametrize("invalid_quarter, expected_msg", [
    ([], "QUARTER_NOT_STR"),
    (123, "QUARTER_NOT_STR"),
    (None, "QUARTER_NOT_STR"),
    ("Q5", "QUARTER_FORMAT_INVALID"),
    ("q1", "QUARTER_FORMAT_INVALID"),
    ("1", "QUARTER_FORMAT_INVALID"),
])
def test_deal_quarter_validation(invalid_quarter, expected_msg):
    deal = Deal("CompanyTech")
    with pytest.raises(AssertionError) as exc:
        deal.process_logics_and_cfo_data("2026", invalid_quarter, {}, {})
    assert str(exc.value) == expected_msg