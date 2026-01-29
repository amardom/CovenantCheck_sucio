import pytest
from app.utils.postprocessing import find_max_stress
from app.core.portfolio import create_portfolio

def test_find_max_stress():

    clients = ["companyHealth", "companyRealEstate", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/Fund_01")

    results = find_max_stress(portfolio, clients, "2025", "Q4", target_var="revenue", step=0.01)