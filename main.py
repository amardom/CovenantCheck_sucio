from app.core.portfolio import create_portfolio

def main():

    clients = ["CompanyTech"]
    years = ["2026"]
    quarters = ["Q1"]

    portfolio = create_portfolio(clients, years, quarters)

if __name__ == "__main__":
    main()