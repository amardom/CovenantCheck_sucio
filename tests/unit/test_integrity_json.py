import pytest
from app.utils.integrity_json import validate_json

FILENAME = "logics_NETFLIX.json"

VALID_LOGICS = {
    "source_file": FILENAME,
    "variables": [{"name": "ebitda", "context": "LTM"}],
    "logical_conditions": [{
        "id": 1, 
        "formula": "ebitda > 0", 
        "evidence": "Section 5.03", 
        "page": 45
    }]
}

def test_validate_json_success():
    """Should pass without raising any AssertionError."""
    validate_json(FILENAME, VALID_LOGICS)

def test_validate_json_wrong_filename():
    """Should explode if the source_file doesn't match the actual filename."""
    data = VALID_LOGICS.copy()
    data["source_file"] = "wrong_name.json"
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

def test_validate_json_empty_variables():
    """Should explode if variables list is empty."""
    data = VALID_LOGICS.copy()
    data["variables"] = []
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

def test_validate_json_empty_logical_conditions():
    """Should explode if variables list is empty."""
    data = VALID_LOGICS.copy()
    data["logical_conditions"] = []
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

def test_validate_json_missing_keys_in_variable():
    """Should explode if a variable is missing the 'name' or 'context' key."""
    data = VALID_LOGICS.copy()
    data["variables"] = [{"name": "ebitda"}], # Missing 'context'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

    data = VALID_LOGICS.copy()
    data["variables"] = [{"context": "income before itda"}], # Missing 'name'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

def test_validate_json_missing_keys_in_logical_conditions():
    """Should explode if a logical condition is missing required keys like 'formula'."""
    data = VALID_LOGICS.copy()
    data["logical_conditions"] = [{"id": 1, "formula": "ratio <= 2.1", "evidence": "text"}] # Missing 'page'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

    data = VALID_LOGICS.copy()
    data["logical_conditions"] = [{"id": 1, "formula": "ratio <= 2.1", "page": 31}] # Missing 'evidence'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

    data = VALID_LOGICS.copy()
    data["logical_conditions"] = [{"id": 1, "evidence": "text", "page": 31}] # Missing 'formula'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)
    
    data = VALID_LOGICS.copy()
    data["logical_conditions"] = [{"formula": "ratio <= 2.1", "evidence": "text", "page": 31}] # Missing 'id'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)