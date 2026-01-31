import pytest, copy
from app.core.z3_engine import validate_json

# Caso de éxito base
VALID_LOGICS = {
    "audit_id": "ClientAlpha_2026_Q1.json",
    "contract_name": "Real Contrato",
    "variables": [{"name": "ebitda", "definition": "LTM", "definition_page": 7}],
    "logical_conditions": [{"id": 1, "formula": "ebitda > 0", "evidence": "S5", "evidence_page": 45}]
}

def test_validate_json_success():
    validate_json(VALID_LOGICS)

@pytest.mark.parametrize("invalid_input, expected_msg", [
    ([], "LOGICS_NOT_A_DICT"),
    ("not a dict", "LOGICS_NOT_A_DICT"),
    (None, "LOGICS_NOT_A_DICT"),
    # Missing Keys
    ({k: v for k, v in VALID_LOGICS.items() if k != "audit_id"}, "AUDIT_ID_IS_MISSING"),
    ({k: v for k, v in VALID_LOGICS.items() if k != "contract_name"}, "CONTRACT_NAME_IS_MISSING"),
    ({k: v for k, v in VALID_LOGICS.items() if k != "variables"}, "VARIABLES_IS_MISSING"),
    # Tipos y Vacíos de Root Keys
    ({**VALID_LOGICS, "audit_id": 123}, "AUDIT_ID_NOT_STR"),
    ({**VALID_LOGICS, "audit_id": ""}, "AUDIT_ID_IS_EMPTY"),
    ({**VALID_LOGICS, "contract_name": True}, "CONTRACT_NAME_NOT_STR"),
    ({**VALID_LOGICS, "contract_name": ""}, "CONTRACT_NAME_IS_EMPTY"),
    ({**VALID_LOGICS, "variables": []}, "VARIABLES_IS_EMPTY"),
])
def test_validate_json_root_errors(invalid_input, expected_msg):
    with pytest.raises(AssertionError) as exc:
        validate_json(invalid_input)
    assert str(exc.value) == expected_msg

@pytest.mark.parametrize("list_key, patch, expected_msg", [
    # Sabotajes en 'variables'
    ("variables", {"name": None}, "NAME_IS_MISSING"),
    ("variables", {"name": 123}, "NAME_NOT_STR"),
    ("variables", {"name": ""}, "NAME_IS_EMPTY"),
    ("variables", {"definition": None}, "DEFINITION_IS_MISSING"),
    ("variables", {"definition": True}, "DEFINITION_NOT_STR"),
    ("variables", {"definition": ""}, "DEFINITION_IS_EMPTY"),
    ("variables", {"definition_page": None}, "DEFINITION_PAGE_IS_MISSING"),
    ("variables", {"definition_page": "p7"}, "DEFINITION_PAGE_NOT_INT"),
    ("variables", {"definition_page": 0}, "DEFINITION_PAGE_IS_BELOW_ONE"),

    # Sabotajes en 'logical_conditions'
    ("logical_conditions", {"id": None}, "ID_IS_MISSING"),
    ("logical_conditions", {"id": "1"}, "ID_NOT_INT"),
    ("logical_conditions", {"id": 0}, "ID_IS_BELOW_ONE"),
    ("logical_conditions", {"formula": None}, "FORMULA_IS_MISSING"),
    ("logical_conditions", {"formula": False}, "FORMULA_NOT_STR"),
    ("logical_conditions", {"formula": ""}, "FORMULA_IS_EMPTY"),
    ("logical_conditions", {"evidence": None}, "EVIDENCE_IS_MISSING"),
    ("logical_conditions", {"evidence": 1.1}, "EVIDENCE_NOT_STR"),
    ("logical_conditions", {"evidence": ""}, "EVIDENCE_IS_EMPTY"),
    ("logical_conditions", {"evidence_page": None}, "EVIDENCE_PAGE_IS_MISSING"),
    ("logical_conditions", {"evidence_page": "45"}, "EVIDENCE_PAGE_NOT_INT"),
    ("logical_conditions", {"evidence_page": -1}, "EVIDENCE_PAGE_IS_BELOW_ONE"),
])
def test_validate_json_list_details(list_key, patch, expected_msg):
    logics = copy.deepcopy(VALID_LOGICS)
    target_item = logics[list_key][0]
    
    for k, v in patch.items():
        if v is None: del target_item[k]
        else: target_item[k] = v

    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == expected_msg

@pytest.mark.parametrize("duplicate_type, expected_msg", [
    ("variable", "DUPLICATES_IN_VARIABLES"),
    ("logic_id", "DUPLICATES_IN_LOGICAL_CONDITIONS"),
])

def test_validate_json_duplicates(duplicate_type, expected_msg):
    logics = copy.deepcopy(VALID_LOGICS)
    if duplicate_type == "variable":
        logics["variables"].append(logics["variables"][0])
    else:
        logics["logical_conditions"].append(logics["logical_conditions"][0])

    with pytest.raises(AssertionError) as exc:
        validate_json(logics)
    assert str(exc.value) == expected_msg