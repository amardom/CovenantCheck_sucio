from app.core.portfolio import create_portfolio
from app.utils.report import generate_portfolio_report, generate_matrix_report
from app.utils.postprocessing import calculate_stress_matrix

def main():

    # We define clients and periods.
    clients = ["companyHealth", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    # We create and analyse portfolio.
    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/Fund_01")

    ANALYSIS_CONFIG = {
        "companyHealth": ["leverage_ratio", "ebitda"],
        "companyTech": ["leverage_ratio", "ebitda"]
    }

    generate_portfolio_report(portfolio, ANALYSIS_CONFIG, output_path="tests/scenarios/Fund_01/portfolio_executive_summary.pdf")

    # We compute stress matrix for a pair of variables.
    stress_config = {
        "var_x": {"name": "revenue", "direction": "down", "steps": 5, "max_pct": 0.5},
        "var_y": {"name": "operating_expenses", "direction": "up", "steps": 5, "max_pct": 1.0}
    }

    matrix_results = calculate_stress_matrix(portfolio, clients, "2024", "Q1", stress_config)

    stress_config["var_x"]["steps"] = 10
    stress_config["var_y"]["steps"] = 10

    matrix_results_refined = calculate_stress_matrix(portfolio, clients, "2024", "Q1", stress_config)

    for client in matrix_results_refined:

        matrix_results[client]["headroom_x"] = matrix_results_refined[client]["headroom_x"]
        matrix_results[client]["headroom_y"] = matrix_results_refined[client]["headroom_y"]

    generate_matrix_report(matrix_results, output_path="tests/scenarios/Fund_01/portfolio_sensitivity_matrix.pdf")

if __name__ == "__main__":
    main()