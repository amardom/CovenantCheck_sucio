import pytest
#from app.utils.postprocessing import
from app.core.portfolio import create_portfolio
"""
def test_find_max_stress_inputs():
    print("")
    invalid_inputs = [([], "CLIENTS_LIST_EMPTY"),
                    ("a string", "CLIENTS_NOT_A_LIST"),
                    (123, "CLIENTS_NOT_A_LIST"),
                    (None, "CLIENTS_NOT_A_LIST"),
                    ([123], "CLIENT_NOT_A_STR")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            find_max_stress(portfolio, invalid, year, quarter, target_var, step, direction)
        assert str(exc.value)

def test_find_max_stress():

    clients = ["companyHealth", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/Fund_01")

    results = find_max_stress(portfolio, clients, "2025", "Q4", target_var="revenue", step=0.01, direction="down")
    """