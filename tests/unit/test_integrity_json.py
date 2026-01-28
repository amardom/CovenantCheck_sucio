import pytest, copy
from app.core.z3_engine import validate_json

VALID_LOGICS = {
    "audit_id": "ClientAlpha_2026_Q1.json",
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

def test_validate_json_missing_audit_id():
    logics = copy.deepcopy(VALID_LOGICS)
    del logics["audit_id"]
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "AUDIT_ID_IS_MISSING"
    print(f"ERROR: {exc.value}")

def test_validate_json_type_audit_id():
    logics = copy.deepcopy(VALID_LOGICS)
    invalid_inputs = [([], "AUDIT_ID_NOT_STR"),
                    (True, "AUDIT_ID_NOT_STR"),
                    (123, "AUDIT_ID_NOT_STR"),
                    (None, "AUDIT_ID_NOT_STR")]
    for invalid, expected_msg in invalid_inputs:
        with pytest.raises(AssertionError) as exc:
            logics["audit_id"] = invalid
            validate_json(logics)
        assert str(exc.value) == expected_msg
        print(f"ERROR: {exc.value}")

def test_validate_json_empty_audit_id():
    logics = copy.deepcopy(VALID_LOGICS)
    logics["audit_id"] = ""
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "AUDIT_ID_IS_EMPTY"
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

def test_validate_json_empty_contract_name():
    logics = copy.deepcopy(VALID_LOGICS)
    logics["contract_name"] = ""
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "CONTRACT_NAME_IS_EMPTY"
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
        payload["variables"][i]["name"] = True
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "NAME_NOT_STR"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["variables"][i]["name"] = ""
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "NAME_IS_EMPTY"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        del payload["variables"][i]["definition"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition"] = True
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_NOT_STR"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition"] = ""
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_IS_EMPTY"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        del payload["variables"][i]["definition_page"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_PAGE_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition_page"] = ""
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_PAGE_NOT_INT"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["variables"][i]["definition_page"] = 0
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "DEFINITION_PAGE_IS_BELOW_ONE"
        print(f"ERROR: {exc.value}")

def test_validate_json_keys_in_logical_conditions():
    logics = copy.deepcopy(VALID_LOGICS)
    for i in range(len(logics["logical_conditions"])):
        
        payload = copy.deepcopy(logics)
        del payload["logical_conditions"][i]["id"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "ID_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["id"] = ""
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "ID_NOT_INT"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["id"] = 0
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "ID_IS_BELOW_ONE"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        del payload["logical_conditions"][i]["formula"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "FORMULA_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["formula"] = True
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "FORMULA_NOT_STR"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["formula"] = ""
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "FORMULA_IS_EMPTY"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        del payload["logical_conditions"][i]["evidence"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "EVIDENCE_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence"] = True
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "EVIDENCE_NOT_STR"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence"] = ""
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "EVIDENCE_IS_EMPTY"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        del payload["logical_conditions"][i]["evidence_page"]
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "EVIDENCE_PAGE_IS_MISSING"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence_page"] = ""
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "EVIDENCE_PAGE_NOT_INT"
        print(f"ERROR: {exc.value}")

        payload = copy.deepcopy(logics)
        payload["logical_conditions"][i]["evidence_page"] = 0
        with pytest.raises(AssertionError) as exc:
            validate_json(payload)
        assert str(exc.value) == "EVIDENCE_PAGE_IS_BELOW_ONE"
        print(f"ERROR: {exc.value}")

def test_validate_json_duplicates_in_variables():
    logics = copy.deepcopy(VALID_LOGICS)
    logics["variables"].append({
        "name": "ebitda",
        "definition": "Duplicate_ebitda",
        "definition_page": 11})
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "DUPLICATES_IN_VARIABLES"
    print(f"ERROR: {exc.value}")

def test_validate_json_duplicate_logic_ids():
    logics = copy.deepcopy(VALID_LOGICS)
    logics["logical_conditions"].append({
        "id": 1, 
        "formula": "x > 1", 
        "evidence": "Duplicate_ID", 
        "evidence_page": 120})
    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == "DUPLICATES_IN_LOGICAL_CONDITIONS"
    print(f"ERROR: {exc.value}")