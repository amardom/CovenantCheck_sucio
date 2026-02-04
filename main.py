from app.core.portfolio import create_portfolio
from app.core.report import generate_portfolio_report, generate_matrix_report
from app.core.postprocessing import calculate_stress_matrix

def main(clients,
        years,
        quarters,
        root_path,
        analysis_config,
        y_stress,
        q_stress,
        stress_config,
        steps_x_refined,
        steps_y_refined):

    portfolio = create_portfolio(clients, years, quarters, root_path)
    generate_portfolio_report(portfolio, analysis_config, f"{root_path}/portfolio_executive_summary.pdf")

    matrix_results = calculate_stress_matrix(portfolio, clients, y_stress, q_stress, stress_config)

    stress_config["var_x"]["steps"] = steps_x_refined
    stress_config["var_y"]["steps"] = steps_y_refined
    
    matrix_results_refined = calculate_stress_matrix(portfolio, clients, y_stress, q_stress, stress_config)

    for client in matrix_results_refined:

        matrix_results[client]["headroom_x"] = matrix_results_refined[client]["headroom_x"]
        matrix_results[client]["headroom_y"] = matrix_results_refined[client]["headroom_y"]
    
    generate_matrix_report(matrix_results, y_stress, q_stress, f"{root_path}/portfolio_sensitivity_matrix_{y_stress}_{q_stress}.pdf")

    return True

if __name__ == "__main__":
    main()