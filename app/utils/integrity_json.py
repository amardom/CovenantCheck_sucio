def validate_json(filename_logics, logics):

    assert "source_file" in logics
    assert type(logics["source_file"]) is str and len(logics["source_file"]) > 0

    assert logics['source_file'] == filename_logics

    assert "contract_name" in logics
    assert type(logics["contract_name"]) is str and len(logics["contract_name"]) > 0

    assert "variables" in logics and len(logics["variables"]) > 0
    assert "logical_conditions" in logics and len(logics["logical_conditions"]) > 0

    for var in logics["variables"]:
        assert "name" in var
        assert "context" in var

        assert type(var["name"]) is str and len(var["name"]) > 0
        assert type(var["context"]) is str and len(var["context"]) > 0

    for var in logics["logical_conditions"]:
        assert "id" in var
        assert "formula" in var
        assert "evidence" in var
        assert "page" in var

        assert type(var["id"]) is int and var["id"] > 0
        assert type(var["formula"]) is str and len(var["formula"]) > 0
        assert type(var["evidence"]) is str and len(var["evidence"]) > 0
        assert type(var["page"]) is int and var["page"] > 0

    print("json validated.")