import pytest
from app.core.portfolio import process_portfolio

def test_portfolio_inputs():

    with pytest.raises(AssertionError):
        process_portfolio([], ["2026"], ["Q1"])
        
    with pytest.raises(AssertionError):
        process_portfolio(["Netflix"], [], ["Q5"])

    with pytest.raises(AssertionError):
        process_portfolio(["Netflix"], ["2026"], [])