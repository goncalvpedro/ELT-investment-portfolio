from api.extractor import Portfolio
import pandas as pd
from middleware._transform import Wallet

portfolio = pd.read_json('portfolio.json')

wallet = Wallet(portfolio)

def update_data():
    portfolio = Portfolio("portfolio.json")
    portfolio.build_historic_data()
    portfolio.build_dividends_data()
    portfolio.save_aggregated_data()


if __name__ == '__main__':
    update_data()
    test = wallet.build_wallet()
    print(test)