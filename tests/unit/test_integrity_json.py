import pytest
from app.utils.integrity_json import validate_json

LOGIC_VALIDA = {
    "source_file": "contrato_real.json",
    "contract_name": "Senior Facility Agreement",
    "variables": [{"name": "ebitda"}, {"name": "net_debt"}],
    "logical_conditions": [
        {"id": 1, "formula": "ebitda > 0", "evidence": "EBITDA must be positive"}
    ]
}

LOGIC_SIN_FORMULA = {
    "source_file": "contrato_real.json",
    "contract_name": "Test",
    "variables": [],
    "logical_conditions": [{"id": 1, "evidence": "falta la clave formula"}]
}

def test_validate_json_ok():
    """Caso de éxito: Todo coincide."""
    # Simplemente llamamos a la función con la estructura de datos
    validate_json("contrato_real.json", LOGIC_VALIDA)

def test_validate_json_error_nombre():
    """Caso de fallo: El nombre del archivo no coincide con el source_file."""
    with pytest.raises(AssertionError):
        # Le pasamos un nombre de archivo que NO es "contrato_real.json"
        validate_json("otro_nombre_distinto.json", LOGIC_VALIDA)

def test_validate_json_error_estructura():
    """Caso de fallo: Falta una clave obligatoria ('formula')."""
    with pytest.raises(KeyError):
        validate_json("contrato_real.json", LOGIC_SIN_FORMULA)

def test_validate_json_lista_vacia():
    """Caso de borde: Lista de variables vacía (sigue siendo válido para la estructura)."""
    logic_vacia = LOGIC_VALIDA.copy()
    logic_vacia["variables"] = []
    validate_json("contrato_real.json", logic_vacia)