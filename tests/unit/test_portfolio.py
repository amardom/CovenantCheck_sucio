import pytest
from app.core.portfolio import create_portfolio

def test_portfolio_inputs():

    with pytest.raises(AssertionError):
        create_portfolio([], ["2026"], ["Q1"])
        
    with pytest.raises(AssertionError):
        create_portfolio(["Netflix"], [], ["Q5"])

    with pytest.raises(AssertionError):
        create_portfolio(["Netflix"], ["2026"], [])