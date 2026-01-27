import pytest, copy
from app.core.z3_engine import validate_json

VALID_LOGICS = {
    "source_file": "logics.json",
    "contract_name": "Real Contrato",
    "variables": [{
        "name": "ebitda",
        "definition": "LTM",
        "definition_page": 7}],
    "logical_conditions": [{
        "id": 1, 
        "formula": "ebitda > 0", 
        "evidence": "Section 5.03", 
        "evidence_page": 45
    }]
}

def test_validate_json_success():
    validate_json(VALID_LOGICS)

def test_validate_json_input_not_a_dict():
    invalid_inputs = [([], "LOGICS_NOT_A_DICT"),
                    ("not a dict", "LOGICS_NOT_A_DICT"),
                    (123, "LOGICS_NOT_A_DICT"),
                    (None, "LOGICS_NOT_A_DICT")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            validate_json(invalid)
        assert str(exc.value) == expected_msg
        print(f"ERROR: {exc.value}")

def test_validate_json_missing_contract_name():
    logics = copy.deepcopy(VALID_LOGICS)
    del logics["contract_name"]
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "CONTRACT_NAME_IS_MISSING"
    print(f"ERROR: {exc.value}")

def test_validate_json_type_contract_name():
    logics = copy.deepcopy(VALID_LOGICS)
    invalid_inputs = [([], "CONTRACT_NAME_NOT_STR"),
                    (True, "CONTRACT_NAME_NOT_STR"),
                    (123, "CONTRACT_NAME_NOT_STR"),
                    (None, "CONTRACT_NAME_NOT_STR")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            logics["contract_name"] = invalid
            validate_json(logics)
        assert str(exc.value) == expected_msg
        print(f"ERROR: {exc.value}")

def test_validate_json_missing_variables():
    logics = copy.deepcopy(VALID_LOGICS)
    del logics["variables"]
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "VARIABLES_IS_MISSING"
    print(f"ERROR: {exc.value}")

def test_validate_json_empty_variables():
    logics = copy.deepcopy(VALID_LOGICS)
    logics["variables"] = []
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "VARIABLES_IS_EMPTY"
    print(f"ERROR: {exc.value}")

def test_validate_json_keys_in_variable():
    logics = copy.deepcopy(VALID_LOGICS)
    for i in range(len(logics["variables"])):
        
        payload = copy.deepcopy(logics)
        del payload["variables"][i]["name"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "NAME_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        del payload["variables"][i]["definition"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        del payload["variables"][i]["definition_page"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_PAGE_IS_MISSING"
        print(f"ERROR: {exc.value}")
"""
def test_validate_json_empty_logical_conditions():
    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = []
    with pytest.raises(AssertionError):
        validate_json(logics)

def test_validate_json_missing_keys_in_variable():
    logics = VALID_LOGICS.copy()
    logics["variables"] = [{"name": "ebitda"}, {"definition": "income before itda"}] # Missing 'definition_page'
    with pytest.raises(AssertionError):
        validate_json(logics)

    logics = VALID_LOGICS.copy()
    logics["variables"] = [{"name": "ebitda"}, {"definition_page": "6"}] # Missing 'definition'
    with pytest.raises(AssertionError):
        validate_json(logics)
    
    logics = VALID_LOGICS.copy()
    logics["variables"] = [{"definition": "income before itda"}, {"definition_page": "6"}] # Missing 'name'
    with pytest.raises(AssertionError):
        validate_json(logics)

def test_validate_json_types_in_variable():
    logics = copy.deepcopy(VALID_LOGICS)

    for i in range(len(logics["variables"])):
        
        payload = copy.deepcopy(logics)
        payload["variables"][i]["name"] = True
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["variables"][i]["name"] = ""
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition"] = True
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition"] = ""
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition_page"] = "1"
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition_page"] = 0
        with pytest.raises(AssertionError):
            validate_json(payload)

def test_validate_json_missing_keys_in_logical_conditions():
    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"id": 1, "formula": "ratio <= 2.1", "evidence": "text"}] # Missing 'evidence_page'
    with pytest.raises(AssertionError):
        validate_json(logics)

    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"id": 1, "formula": "ratio <= 2.1", "evidence_page": 31}] # Missing 'evidence'
    with pytest.raises(AssertionError):
        validate_json(logics)

    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"id": 1, "evidence": "text", "evidence_page": 31}] # Missing 'formula'
    with pytest.raises(AssertionError):
        validate_json(logics)
    
    logics = VALID_LOGICS.copy()
    logics["logical_conditions"] = [{"formula": "ratio <= 2.1", "evidence": "text", "evidence_page": 31}] # Missing 'id'
    with pytest.raises(AssertionError):
        validate_json(logics)

def test_validate_json_types_in_logical_conditions():
    logics = copy.deepcopy(VALID_LOGICS)

    for i in range(len(logics["logical_conditions"])):
        
        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["id"] = "1"
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["id"] = 0
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence"] = True
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence"] = ""
        with pytest.raises(AssertionError):
            validate_json(payload)
        
        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["formula"] = True
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["formula"] = ""
        with pytest.raises(AssertionError):
            validate_json(payload)
        
        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence_page"] = "1"
        with pytest.raises(AssertionError):
            validate_json(payload)

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence_page"] = 0
        with pytest.raises(AssertionError):
            validate_json(payload)

def test_validate_json_duplicate_variable_names():
    logics = copy.deepcopy(VALID_LOGICS)
    # Duplicamos la variable para ver si explota
    logics["variables"].append({"name": "ebitda", "context": "Duplicate"})
    with pytest.raises(AssertionError):
        validate_json(logics)

def test_validate_json_duplicate_logic_ids():
    logics = copy.deepcopy(VALID_LOGICS)
    # Duplicamos el ID de la condición
    logics["logical_conditions"].append({
        "id": 1, 
        "formula": "x > 1", 
        "evidence": "Duplicate ID", 
        "page": 10
    })
    with pytest.raises(AssertionError):
        validate_json(logics) """