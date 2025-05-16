from datetime import datetime as dt
from typing import Optional
import yfinance as yf
import pandas as pd
import os

class Asset:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self._yf_asset = yf.Ticker(ticker)

    def get_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None, period: Optional[str] = None) -> Optional[pd.DataFrame]:
        try:
            if period:
                return self._yf_asset.history(period=period)
            return self._yf_asset.history(start=start_date, end=end_date)
        except Exception as e:
            print(f"[ERROR] Failed to fetch history for {self.ticker}: {e}")
            return None

    def get_dividends(self) -> Optional[pd.Series]:
        try:
            return self._yf_asset.dividends
        except Exception as e:
            print(f"[ERROR] Failed to fetch dividends for {self.ticker}: {e}")
            return None


class Portfolio:
    def __init__(self, file_path: str):
        self.data = self._load_portfolio(file_path)
        self.historic_prices = pd.DataFrame()
        self.dividends = pd.DataFrame()

    @staticmethod
    def _load_portfolio(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_json(file_path)
        except Exception as e:
            print(f"[ERROR] Failed to read portfolio file: {e}")
            return pd.DataFrame()

    @staticmethod
    def _validate_date(date_str: str) -> dt.date:
        return dt.strptime(date_str, '%Y-%m-%d').date()

    @staticmethod
    def _save_to_csv(data: pd.DataFrame, filename: str):
        output_folder = 'output'
        filename = f"{output_folder}/{filename}.csv"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        data.to_csv(filename)

    def build_historic_data(self):
        today = dt.today()

        for _, row in self.data.iterrows():
            ticker = row['ticker']
            start_date = self._validate_date(row['first_acquisition'])

            asset = Asset(ticker)
            history = asset.get_history(start_date=start_date, end_date=today)

            if history is not None and 'Close' in history:
                close_prices = history['Close']
                close_prices.name = ticker
                self.historic_prices = self.historic_prices.join(close_prices, how='outer')
                # self._save_to_csv(history, ticker)

    def build_dividends_data(self):
        try:
            for _,row in self.data.iterrows():
        
                ticker = row['ticker']
                
                asset = Asset(ticker)
                dividends = asset.get_dividends()
                if dividends is not None:
                    adjusted_dividends = pd.Series(dividends, name=ticker)
                    self.dividends = self.dividends.join(adjusted_dividends, how='outer')
                    file_name = f'{ticker}_dividends'
                    # self._save_to_csv(adjusted_dividends, file_name)
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch dividends: {e}")
            return None

    def save_aggregated_data(self):
        self._save_to_csv(self.historic_prices, 'prices')
        self._save_to_csv(self.dividends, 'dividends')

if __name__ == "__main__":
    portfolio = Portfolio("portfolio.json")
    portfolio.build_historic_data()
    portfolio.build_dividends_data()
    portfolio.save_aggregated_data()
