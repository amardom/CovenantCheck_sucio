import pytest
from app.utils.integrity_json import validate_json

FILENAME = "logics_NETFLIX.json"

VALID_LOGICS = {
    "source_file": FILENAME,
    "contract_name": "Real Contrato",
    "variables": [{"name": "ebitda", "context": "LTM"}],
    "logical_conditions": [{
        "id": 1, 
        "formula": "ebitda > 0", 
        "evidence": "Section 5.03", 
        "page": 45
    }]
}

def test_validate_json_success():
    validate_json(FILENAME, VALID_LOGICS)

def test_validate_json_empty_source_file():
    logics = VALID_LOGICS.copy()
    logics["source_file"] = []
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_type_source_file():
    logics = VALID_LOGICS.copy()
    logics["source_file"] = True
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_wrong_filename():
    logics = VALID_LOGICS.copy()
    logics["source_file"] = "wrong_name.json"
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_empty_contract_name():
    logics = VALID_LOGICS.copy()
    logics["contract_name"] = []
    print(logics["contract_name"])
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_type_contract_name():
    logics = VALID_LOGICS.copy()
    logics["contract_name"] = True
    print(logics["contract_name"])
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_empty_variables():
    logics = VALID_LOGICS.copy()
    logics["variables"] = []
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_empty_logical_conditions():
    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = []
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_missing_keys_in_variable():
    logics = VALID_LOGICS.copy()
    logics["variables"] = [{"name": "ebitda"}] # Missing 'context'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

    logics = VALID_LOGICS.copy()
    logics["variables"] = [{"context": "income before itda"}] # Missing 'name'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_types_in_variable():
    logics = VALID_LOGICS.copy()
    for var in logics["variables"]:
        var["name"] = True
        with pytest.raises(AssertionError):
            validate_json(FILENAME, logics)
        var["context"] = True
        with pytest.raises(AssertionError):
            validate_json(FILENAME, logics)

def test_validate_json_missing_keys_in_logical_conditions():
    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"id": 1, "formula": "ratio <= 2.1", "evidence": "text"}] # Missing 'page'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"id": 1, "formula": "ratio <= 2.1", "page": 31}] # Missing 'evidence'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"id": 1, "evidence": "text", "page": 31}] # Missing 'formula'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)
    
    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"formula": "ratio <= 2.1", "evidence": "text", "page": 31}] # Missing 'id'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, logics)

def test_validate_json_types_in_logical_conditions():
    logics = VALID_LOGICS.copy()
    for var in logics["logical_conditions"]:
        var["id"] = "1"
        with pytest.raises(AssertionError):
            validate_json(FILENAME, logics)
        var["evidence"] = True
        with pytest.raises(AssertionError):
            validate_json(FILENAME, logics)
        var["formula"] = True
        with pytest.raises(AssertionError):
            validate_json(FILENAME, logics)
        var["formula"] = "1"
        with pytest.raises(AssertionError):
            validate_json(FILENAME, logics)