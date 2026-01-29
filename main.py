from app.core.portfolio import create_portfolio
from app.utils.report import generate_portfolio_report, generate_stress_report
from app.utils.postprocessing import find_max_stress

def main():

    clients = ["companyHealth", "companyRealEstate", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters, root_path="tests/scenarios/Fund_01")

    ANALYSIS_CONFIG = {
        "companyHealth": ["leverage_ratio", "ebitda"],
        "companyRealEstate": ["leverage_ratio"],
        "companyTech": ["leverage_ratio", "ebitda"]
    }

    generate_portfolio_report(portfolio, ANALYSIS_CONFIG, output_path="tests/scenarios/Fund_01/portfolio_executive_summary.pdf")

    stress_results = find_max_stress(portfolio, clients, "2024", "Q1", target_var="revenue", step=0.01)

    generate_stress_report(stress_results, output_path="tests/scenarios/Fund_01/portfolio_stress_summary.pdf")

if __name__ == "__main__":
    main()