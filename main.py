from app.core.portfolio import create_portfolio
from app.utils.report_pdf import generate_portfolio_report

def main():

    clients = ["companyHealth", "companyRealEstate", "companyTech"]
    years = ["2024", "2025"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    portfolio = create_portfolio(clients, years, quarters)

    ANALYSIS_CONFIG = {
    "companyHealth": ["leverage_ratio", "ebitda"],
    "companyRealEstate": ["leverage_ratio"],
    "companyTech": ["leverage_ratio", "ebitda"]
    }

    generate_portfolio_report(portfolio, ANALYSIS_CONFIG, output_path="portfolio_executive_summary.pdf")

if __name__ == "__main__":
    main()