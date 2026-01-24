import pytest
from app.core.portfolio import create_portfolio

def test_portfolio_inputs():

    with pytest.raises(AssertionError) as exc:
        create_portfolio([], ["2026"], ["Q1"], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio("Netflix", ["2026"], ["Q1"], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")
        
    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], [], ["Q4"], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], "2026", ["Q4"], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["26"], ["Q4"], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], [], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], "Q3", "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], ["Q5"], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], ["Q3"], str())
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], ["Q6"], ["tests/scenarios/deal"])
    print(f"\nERROR: {exc.value}")

    with pytest.raises(AssertionError) as exc:
        create_portfolio(["Netflix"], ["2026"], ["Q3" "Q5"], "tests/scenarios/deal")
    print(f"\nERROR: {exc.value}")

def test_portfolio_indexing():
    return
    clients = ["companyHealth", "companyRealEstate", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/deal")

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