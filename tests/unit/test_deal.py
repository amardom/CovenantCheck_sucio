import pytest
from app.core.deal import Deal

def test_deal_full_flow():

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
        "consolidated_ebitda": 2000000.0,
        "consolidated_net_debt": 4000000.0
    }

    deal.process_logics_and_cfo_data(year, quarter, logics_mock, cfo_data_mock)

    assert deal.id == client_id
    assert year in deal.history
    assert quarter in deal.history[year]
    
    entry = deal.history[year][quarter]

    assert len(entry["cfo_data"]) == 2
    assert entry["cfo_data"]["consolidated_ebitda"] == 2000000.0
    assert entry["cfo_data"]["consolidated_net_debt"] == 4000000.0

    assert len(entry["logics"]) == 4
    assert entry["logics"]["audit_id"] == f"{client_id}_{year}_{quarter}"
    assert entry["logics"]["contract_name"] == "Credit Agreement - NETFLIX, INC. (2009)"
    assert entry["logics"]["variables"][0]["name"] == "consolidated_ebitda"
    assert entry["logics"]["variables"][0]["definition"] == "Calculated EBITDA"
    assert entry["logics"]["variables"][0]["definition_page"] == 9
    assert entry["logics"]["variables"][1]["name"] == "consolidated_net_debt"
    assert entry["logics"]["variables"][1]["definition"] == "Total debt minus cash"
    assert entry["logics"]["variables"][1]["definition_page"] == 19
    assert entry["logics"]["variables"][2]["name"] == "consolidated_leverage_ratio"
    assert entry["logics"]["variables"][2]["definition"] == "Leverage Ratio"
    assert entry["logics"]["variables"][2]["definition_page"] == 29
    assert entry["logics"]["logical_conditions"][0]["formula"] == "consolidated_leverage_ratio == consolidated_net_debt / consolidated_ebitda"
    assert entry["logics"]["logical_conditions"][0]["evidence"] == "Section 1.01"
    assert entry["logics"]["logical_conditions"][0]["evidence_page"] == 10
    assert entry["logics"]["logical_conditions"][1]["formula"] == "consolidated_leverage_ratio <= 2.5"
    assert entry["logics"]["logical_conditions"][1]["evidence"] == "Section 7.12"
    assert entry["logics"]["logical_conditions"][1]["evidence_page"] == 11
    assert entry["z3_result"]["is_compliant"] == True
    assert entry["z3_result"]["norm_metric"] == pytest.approx(1423525)
    
VALID_ID = "CompanyTech"
VALID_YEAR = "2026"
VALID_QUARTER = "Q1"

@pytest.mark.parametrize("id, y, q, logics, cfo_data, expected_msg", [
    ([], VALID_YEAR, VALID_QUARTER, {}, {}, "ID_NOT_STR"),
    (123, VALID_YEAR, VALID_QUARTER, {}, {}, "ID_NOT_STR"),
    (None, VALID_YEAR, VALID_QUARTER, {}, {}, "ID_NOT_STR"),
    ("", VALID_YEAR, VALID_QUARTER,  {}, {}, "ID_EMPTY"),
    (VALID_ID, [], VALID_QUARTER, {}, {}, "YEAR_NOT_STR"),
    (VALID_ID, 123, VALID_QUARTER, {}, {}, "YEAR_NOT_STR"),
    (VALID_ID, None, VALID_QUARTER, {}, {}, "YEAR_NOT_STR"),
    (VALID_ID, "26", VALID_QUARTER,  {}, {}, "YEAR_FORMAT_INVALID"),
    (VALID_ID, "20265", VALID_QUARTER, {}, {}, "YEAR_FORMAT_INVALID"),
    (VALID_ID, VALID_YEAR, [], {}, {}, "QUARTER_NOT_STR"),
    (VALID_ID, VALID_YEAR, 123, {}, {}, "QUARTER_NOT_STR"),
    (VALID_ID, VALID_YEAR, None, {}, {}, "QUARTER_NOT_STR"),
    (VALID_ID, VALID_YEAR, "Q5", {}, {}, "QUARTER_FORMAT_INVALID"),
    (VALID_ID, VALID_YEAR, "q1", {}, {}, "QUARTER_FORMAT_INVALID"),
    (VALID_ID, VALID_YEAR, "1", {}, {}, "QUARTER_FORMAT_INVALID"),
    (VALID_ID, VALID_YEAR, VALID_QUARTER, "NotDict", {}, "LOGICS_NOT_DICT"),
    (VALID_ID, VALID_YEAR, VALID_QUARTER, {}, "NotDict", "CFO_DATA_NOT_DICT"),
])
def test_deal_inputs(id, y, q, logics, cfo_data, expected_msg):
    with pytest.raises(AssertionError) as exc:
        deal = Deal(id)
        deal.process_logics_and_cfo_data(y, q, logics, cfo_data)
    assert str(exc.value) == expected_msg