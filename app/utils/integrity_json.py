def validate_json(filename_logics, logics):

    assert "source_file" in logics
    assert "variables" in logics
    assert "logical_conditions" in logics

    assert logics['source_file'] == filename_logics
    
    assert len(logics["variables"]) > 0
    assert len(logics["logical_conditions"]) > 0

    for var in logics["variables"]:
        assert "name" in var
        assert "context" in var

    for var in logics["logical_conditions"]:
        assert "id" in var
        assert "formula" in var
        assert "evidence" in var
        assert "page" in var

    print("json validated.")