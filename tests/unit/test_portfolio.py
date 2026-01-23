import pytest
from app.core.portfolio import create_portfolio

def test_portfolio_inputs():

    with pytest.raises(AssertionError):
        create_portfolio([], ["2026"], ["Q1"])
        
    with pytest.raises(AssertionError):
        create_portfolio(["Netflix"], [], ["Q5"])

    with pytest.raises(AssertionError):
        create_portfolio(["Netflix"], ["2026"], [])

def test_portfolio_indexing():
    
    clients = ["companyHealth", "companyRealEstate", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters)

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
                
                assert "is_compliant" in entry["z3_result"]
                assert isinstance(entry["z3_result"]["is_compliant"], bool)