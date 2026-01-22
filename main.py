from app.core.portfolio import process_portfolio

def main():

    clients = ["CompanyTech"]
    years = ["2026"]
    quarters = ["Q1"]

    portfolio = process_portfolio(clients, years, quarters)

if __name__ == "__main__":
    main()