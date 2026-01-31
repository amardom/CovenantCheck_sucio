from app.core.portfolio import create_portfolio
from app.core.report import generate_portfolio_report, generate_matrix_report
from app.core.postprocessing import calculate_stress_matrix

CLIENTS = ["TechGrowth"]
YEARS = ["2024", "2025"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
ROOT_PATH = "tests/scenarios/Fund_02"

ANALYSIS_CONFIG = {
    "TechGrowth": ["leverage_ratio", "ebitda"]
}

# STRESS PARAMETERS
VAR_X_NAME = "revenue"
VAR_Y_NAME = "operating_expenses"
DIRECTION_X = "down"
DIRECTION_Y = "up"
STEPS_X = 5
STEPS_Y = 5
STEPS_X_REFINED = 10 
STEPS_Y_REFINED = 10
MAX_PCT_X = 0.2
MAX_PCT_Y = 0.2
Y = "2024"
Q = "Q1"

STRESS_CONFIG = {
    "var_x": {"name": f"{VAR_X_NAME}", "direction": f"{DIRECTION_X}", "steps": STEPS_X, "max_pct": MAX_PCT_X},
    "var_y": {"name": f"{VAR_Y_NAME}", "direction": f"{DIRECTION_Y}", "steps": STEPS_Y, "max_pct": MAX_PCT_Y}
}

def main():

    # We create and analyse portfolio.
    portfolio = create_portfolio(CLIENTS, YEARS, QUARTERS, ROOT_PATH)
    generate_portfolio_report(portfolio, ANALYSIS_CONFIG, f"{ROOT_PATH}/portfolio_executive_summary.pdf")

    # We compute stress matrix for a pair of variables.
    matrix_results = calculate_stress_matrix(portfolio, CLIENTS, Y, Q, STRESS_CONFIG)

    STRESS_CONFIG["var_x"]["steps"] = STEPS_X_REFINED
    STRESS_CONFIG["var_y"]["steps"] = STEPS_Y_REFINED
    
    matrix_results_refined = calculate_stress_matrix(portfolio, CLIENTS, Y, Q, STRESS_CONFIG)

    for client in matrix_results_refined:

        matrix_results[client]["headroom_x"] = matrix_results_refined[client]["headroom_x"]
        matrix_results[client]["headroom_y"] = matrix_results_refined[client]["headroom_y"]
    
    generate_matrix_report(matrix_results, f"{ROOT_PATH}/portfolio_sensitivity_matrix.pdf")

if __name__ == "__main__":
    main()