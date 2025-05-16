from datetime import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import os

# VISUALIZE


def plot_timeseries(data, title="", xlabel="Date", ylabel="Value", grid=True, figsize=(12, 6), legend=True):
    plt.figure(figsize=figsize)

    for column in data.columns:
        plt.plot(data.index, data[column], label=column, linewidth=2)

    plt.xticks(rotation=45, ha='right')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if grid:
        plt.grid(alpha=0.3, linestyle='--')

    if legend:
        plt.legend(loc='best', ncol=2, frameon=False)

    plt.tight_layout()
    plt.show()

# BUILDING


class Wallet():
    def __init__(self, portfolio: pd.DataFrame):
        self.portfolio = portfolio

    def get_files(self, file: str, type=['-d' or '-s'], folder='output') -> pd.DataFrame:
        if type == '-d':
            file = str(f'{file}_dividends')

        file = self._validate_str(file)
        try:
            if file in os.listdir(folder):
                file = pd.read_csv(f'{folder}/{file}')
                return file
            raise FileNotFoundError(f'Check file and folder name.')
        except Exception as e:
            print(f'[ERROR] File not found. {e}')
            return pd.DataFrame()

    def get_data(self, file):
        file = self._validate_str(file)
        folder = 'output'

        try:
            if file in os.listdir(folder):
                file = pd.read_csv(f'{folder}/{file}')
                return file
            raise FileNotFoundError(f'Check file and folder name.')
        except Exception as e:
            print(f'[ERROR] File not found. {e}')
            return pd.DataFrame()

    def _validate_str(self, text: str) -> str:
        validated_str = str(f'{text}.csv')
        return validated_str

    def _filter_df(self, historic_prices, start) -> pd.DataFrame:
        filtered_df = historic_prices.loc[historic_prices['Date'] > start]
        return filtered_df

    def _normalize_df(self, historic_prices: pd.DataFrame) -> pd.DataFrame:
        normalized_df = historic_prices.div(historic_prices.iloc[0])
        return normalized_df

    def _merge_df(self, left_df: pd.DataFrame, right_df: pd.DataFrame, on: str, how='outer') -> pd.DataFrame:
        merged_df = left_df.merge(right_df, how, on)
        return merged_df


    def current_price(self) -> pd.DataFrame:
        tickers = []
        current_prices = []
        for ticker in self.portfolio['ticker']:
            historic_price = self.get_data('prices')
            current_price = historic_price[ticker].iloc[-1]
            tickers.append(ticker)
            current_prices.append(current_price)

        df = pd.DataFrame(
            data={'ticker': tickers, 'current_price': current_prices})

        updated_wallet = self._merge_df(
            self.portfolio, df, on='ticker', how='inner')

        self.portfolio = updated_wallet

    def calculate_equity(self):
        self.portfolio['equity'] = self.portfolio['shares'] * \
            self.portfolio['current_price']

    def calculate_return(self):
        base_price = self.portfolio['price']
        current_price = self.portfolio['current_price']
        self.portfolio['return'] = (
            (current_price - base_price)/base_price) * 100

    # def calculate_dividends(self):
    #     tickers_list = []
    #     dividends_list = []
    #     for _, row in self.portfolio.iterrows():

    #         ticker = row['ticker']
    #         acq_date = row['first_acquisition']

    #         dividends = self.get_files(ticker, '-d')
    #         filtered_dividends = self._filter_df(dividends, acq_date)
    #         dividend = filtered_dividends[ticker].sum()

    #         tickers_list.append(ticker)
    #         dividends_list.append(dividend)

    #     df = pd.DataFrame(data={'ticker': tickers_list,
    #                       'dividends': dividends_list})

    #     self.portfolio = self._merge_df(self.portfolio, df, 'ticker', 'inner')

    #     self.portfolio['dividends'] = self.portfolio['dividends'] * \
    #         self.portfolio['shares']

    def calculate_dividends(self):
        tickers_list = []
        dividends_list = []
        for _, row in self.portfolio.iterrows():

            ticker = row['ticker']
            acq_date = row['first_acquisition']

            dividends = self.get_data('dividends')
            print(dividends)



        #     dividends = pd.DataFrame(dividends[ticker], index=dividends['Date'])
        #     filtered_dividends = self._filter_df(dividends, acq_date)
        #     dividend = filtered_dividends[ticker].sum()

        #     tickers_list.append(ticker)
        #     dividends_list.append(dividend)

        # df = pd.DataFrame(data={'ticker': tickers_list,
        #                         'dividends': dividends_list})

        # self.portfolio = self._merge_df(self.portfolio, df, 'ticker', 'inner')

        # self.portfolio['dividends'] = self.portfolio['dividends'] * \
        #     self.portfolio['shares']

    def calculate_return_dividend(self):
        price = self.portfolio['price']
        dividends = self.portfolio['dividends']
        equity = self.portfolio['equity']
        shares = self.portfolio['shares']

        self.portfolio['return_dividends'] = (
            (((equity + dividends) / shares) - price) / price) * 100

    # def last_dividend(self):
    #     tickers_list = []
    #     dates_list = []
    #     for _, row in self.portfolio.iterrows():

    #         ticker = row['ticker']

    #         dividends = self.get_files(ticker, '-d')
    #         dividends_date = str(dividends['Date'].iloc[-1]).split(' ')[0]

    #         tickers_list.append(ticker)
    #         dates_list.append(dividends_date)

    #     df = pd.DataFrame(data={'ticker': tickers_list,
    #                       'last_dividend': dates_list})

    #     self.portfolio = self._merge_df(self.portfolio, df, 'ticker', 'inner')

    def last_dividend(self):
        tickers_list = []
        dates_list = []
        for _, row in self.portfolio.iterrows():

            ticker = row['ticker']

            dividends = self.get_files(ticker, '-d')
            dividends_date = str(dividends['Date'].iloc[-1]).split(' ')[0]

            tickers_list.append(ticker)
            dates_list.append(dividends_date)

        df = pd.DataFrame(data={'ticker': tickers_list,
                          'last_dividend': dates_list})

        self.portfolio = self._merge_df(self.portfolio, df, 'ticker', 'inner')

    def build_wallet(self):
        # self.current_price()
        # self.calculate_equity()
        # self.calculate_return()
        self.calculate_dividends()
        # self.calculate_return_dividend()
        # self.last_dividend()

        # return self.portfolio


# TESTING

portfolio = pd.read_json('portfolio.json')

wallet = Wallet(portfolio)

test = wallet.build_wallet()

print(test)
