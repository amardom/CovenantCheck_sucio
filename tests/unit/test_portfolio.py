import pytest
from app.core.portfolio import create_portfolio

def test_portfolio_inputs():

    with pytest.raises(AssertionError):
        create_portfolio([], ["2026"], ["Q1"])
        
    with pytest.raises(AssertionError):
        create_portfolio(["Netflix"], [], ["Q5"])

    with pytest.raises(AssertionError):
        create_portfolio(["Netflix"], ["2026"], [])

def test_full_portfolio_indexing():
    # 1. Parámetros de entrada
    clients = ["companyHealth", "companyRealEstate", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    # 2. Ejecución
    # Importante: Asegúrate de que process_portfolio lea de 'tests/scenarios'
    portfolio = create_portfolio(clients, years, quarters)

    # 3. Validar Dimensión 1: Clientes (Longitud del Portfolio)
    assert len(portfolio) == 3, f"Se esperaban 3 clientes, se obtuvieron {len(portfolio)}"
    assert set(portfolio.keys()) == set(clients), "Los IDs de los clientes no coinciden con las keys del portfolio"

    # 4. Validar Dimensión 2 y 3: Años y Quarters por cada cliente
    for client_id in clients:
        deal = portfolio[client_id]
        
        # El historial debe tener exactamente los años pasados
        assert len(deal.history) == len(years)
        
        for year in years:
            assert year in deal.history
            
            for q in quarters:
                # Comprobar que el índice [year][quarter] existe y está poblado
                entry = deal.history[year][q]
                assert entry is not None, f"Fallo en índice: {client_id} -> {year} -> {q} está vacío"
                
                # Validar que los datos pertenecen AL CLIENTE CORRECTO
                # (Evita que los datos de retailCorp se filtren en techGrowth por error de bucle)
                expected_contract = f"{client_id} Strategic Credit Facilities"
                assert entry["logics"]["contract_name"] == expected_contract
                
                # Validar que Z3 procesó cada entrada de forma independiente
                assert "is_compliant" in entry["z3_result"]
                assert isinstance(entry["z3_result"]["is_compliant"], bool)

    print("✅ Validación de índices de Portfolio (3 clientes, 2 años, 4Qs) exitosa.")