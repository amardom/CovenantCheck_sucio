def validate_json(filename_logics, logics):

    assert logics['source_file'] == filename_logics

    _ = logics['contract_name']

    for v in logics['variables']:
        _ = v['name']
        
    for rule in logics['logical_conditions']:
        _ = rule['id']
        _ = rule['formula']
        _ = rule['evidence']
    
    print("json validated.")