import pytest
from app.utils.integrity_json import validate_json  # Adjust the import based on your folder structure

# --- MOCK DATA ---
FILENAME = "netflix_logics.json"

VALID_DATA = {
    "source_file": FILENAME,
    "variables": [{"name": "ebitda", "context": "LTM"}],
    "logical_conditions": [{
        "id": 1, 
        "formula": "ebitda > 0", 
        "evidence": "Section 5.03", 
        "page": 45
    }]
}

# --- TESTS ---

def test_validate_json_success():
    """Should pass without raising any AssertionError."""
    validate_json(FILENAME, VALID_DATA)

def test_validate_json_wrong_filename():
    """Should explode if the source_file doesn't match the actual filename."""
    data = VALID_DATA.copy()
    data["source_file"] = "wrong_name.json"
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

def test_validate_json_empty_variables():
    """Should explode if variables list is empty."""
    data = VALID_DATA.copy()
    data["variables"] = []
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

def test_validate_json_missing_fields_in_variable():
    """Should explode if a variable is missing the 'name' or 'context' key."""
    data = {
        "source_file": FILENAME,
        "variables": [{"name": "ebitda"}], # Missing 'context'
        "logical_conditions": VALID_DATA["logical_conditions"]
    }
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)

def test_validate_json_missing_logic_keys():
    """Should explode if a logical condition is missing required keys like 'formula'."""
    data = VALID_DATA.copy()
    data["logical_conditions"] = [{"id": 1, "evidence": "text"}] # Missing 'formula' and 'page'
    with pytest.raises(AssertionError):
        validate_json(FILENAME, data)