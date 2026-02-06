import pytest
import json
import main

# GENERAL PARAMETERS.
CLIENTS = ["TechCorp", "HealthCorp"]
YEARS = ["2024", "2025"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
ROOT_PATH = "tests/scenarios/Fund_01"
VAR_CONFIG_1 = "leverage_ratio"
VAR_CONFIG_2 = "ebitda"

# STRESS PARAMETERS.
VAR_X_NAME = "revenue"
VAR_Y_NAME = "operating_expenses"
DIRECTION_X = "down"
DIRECTION_Y = "up"
STEPS_X = 4
STEPS_Y = 4
STEPS_X_REFINED = 10 
STEPS_Y_REFINED = 10
MAX_PCT_X = 0.2
MAX_PCT_Y = 0.2
Y = "2024"
Q = "Q1"

ANALYSIS_CONFIG = {c: [f"{VAR_CONFIG_1}", f"{VAR_CONFIG_2}"] for c in CLIENTS}

STRESS_CONFIG = {
    "var_x": {"name": f"{VAR_X_NAME}", "direction": f"{DIRECTION_X}", "steps": STEPS_X, "max_pct": MAX_PCT_X},
    "var_y": {"name": f"{VAR_Y_NAME}", "direction": f"{DIRECTION_Y}", "steps": STEPS_Y, "max_pct": MAX_PCT_Y}
}

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def test_main_full_flow():
    
    res = main.main(CLIENTS,
                YEARS,
                QUARTERS,
                ROOT_PATH,
                ANALYSIS_CONFIG,
                Y,
                Q,
                STRESS_CONFIG,
                STEPS_X_REFINED,
                STEPS_Y_REFINED)
    
    assert res == True