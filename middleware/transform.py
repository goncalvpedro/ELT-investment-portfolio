from pathlib import Path
import pandas as pd
import os
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt


class Wallet():
    def __init__(self):
        self.portfolio = pd.read_json(r'portfolio.json')
        self.dividends = pd.read_csv(r'./output/dividends.csv')
        self.prices = pd.read_csv(r'output/prices.csv')

        self.ticker = self.portfolio['ticker']
        self.shares = self.portfolio['shares']
        self.price = self.portfolio['price']
        self.acq_date = self.portfolio['first_acquisition']

    @staticmethod
    def _validate_str(text: str) -> str:
        validated_str = str(f'{text}.csv')
        return validated_str

    @staticmethod
    def _filter_df(historic_prices, start) -> pd.DataFrame:
        filtered_df = historic_prices.loc[historic_prices['Date'] > start]
        return filtered_df

    @staticmethod
    def _normalize_df(historic_prices: pd.DataFrame) -> pd.DataFrame:
        historic_prices = historic_prices.copy()
        historic_prices['Date'] = pd.to_datetime(historic_prices['Date'], errors='coerce')
        historic_prices.set_index('Date', inplace=True)

        historic_prices = historic_prices.apply(pd.to_numeric, errors='coerce').bfill()

        normalized_df = historic_prices.apply(lambda col: (col / col[col.first_valid_index()] - 1) * 100)

        return normalized_df
    
    @staticmethod
    def _price_return_vs_paid(historic_prices: pd.DataFrame, portfolio_df: pd.DataFrame) -> pd.DataFrame:
        historic_prices['Date'] = pd.to_datetime(historic_prices['Date'], errors='coerce')
        historic_prices.set_index('Date', inplace=True)

        historic_prices = historic_prices.apply(pd.to_numeric, errors='coerce').bfill()

        price_paid = dict(zip(portfolio_df['ticker'], portfolio_df['price']))

        returns_df = pd.DataFrame(index=historic_prices.index)
        for ticker in historic_prices.columns:
            if ticker in price_paid:
                initial_price = price_paid[ticker]
                returns_df[ticker] = (historic_prices[ticker] / initial_price - 1) * 100
            else:
                returns_df[ticker] = float('nan')

        return returns_df
    
    @staticmethod
    def _merge_df(left_df: pd.DataFrame, right_df: pd.DataFrame, on: str, how='outer') -> pd.DataFrame:
        merged_df = left_df.merge(right_df, how, on)
        return merged_df

    def current_price(self) -> pd.DataFrame:
        tickers = []
        current_prices = []
        for ticker in self.ticker:
            current_price = self.prices[ticker].iloc[-1]
            tickers.append(ticker)
            current_prices.append(current_price)

        df = pd.DataFrame(
            data={'ticker': tickers, 'current_price': current_prices})

        updated_wallet = self._merge_df(
            self.portfolio, df, on='ticker', how='inner')

        self.portfolio = updated_wallet

    def calculate_equity(self):
        self.portfolio['equity'] = self.shares * \
            self.portfolio['current_price']

    def calculate_return(self):
        base_price = self.price
        current_price = self.portfolio['current_price']
        self.portfolio['return'] = (
            (current_price - base_price)/base_price) * 100

    def calculate_dividends(self):
        tickers_list = []
        dividends_list = []
        for _, row in self.portfolio.iterrows():
            acq_date = row['first_acquisition']
            ticker = row['ticker']

            filtered_df = self._filter_df(self.dividends, acq_date)
            dividend = filtered_df[ticker].fillna(0).sum()

            tickers_list.append(ticker)
            dividends_list.append(dividend)

        df = pd.DataFrame(data={'ticker': tickers_list,
                                'dividends': dividends_list})

        self.portfolio = self._merge_df(self.portfolio, df, 'ticker', 'inner')

        self.portfolio['dividends'] = self.portfolio['dividends'] * \
            self.shares

    def calculate_return_dividend(self):
        price = self.price
        shares = self.shares
        dividends = self.portfolio['dividends']
        equity = self.portfolio['equity']

        self.portfolio['return_dividends'] = (
            (((equity + dividends) / shares) - price) / price) * 100

    def last_dividend(self):
        tickers_list = []
        tuples_list = []
        for _, row in self.portfolio.iterrows():
            ticker = row['ticker']
            shares = row['shares']
            dividends_df = self.dividends[['Date', ticker]].dropna()

            last_date, last_dividend = dividends_df.iloc[-1]
            tickers_list.append(ticker)
            tuples_list.append(last_date.split(
                ' ')[0])

        df = pd.DataFrame(data={'ticker': tickers_list,
                          'last_dividend': tuples_list})

        self.portfolio = self._merge_df(self.portfolio, df, 'ticker', 'inner')

    def calculate_cagr_individual(self):
        cagr_list = []
        for _, row in self.portfolio.iterrows():
            price = row['price']
            equity = row['current_price'] * row['shares'] + row['dividends']
            invested = row['shares'] * price
            acq_date = row['first_acquisition']
            time_investing = dt.today() - dt.strptime(acq_date, '%Y-%m-%d')
            portfolio_age = int(str(time_investing).split(' ')[0])
            exp = 365.25 / portfolio_age if portfolio_age > 0 else 1
            cagr = ((((equity / invested)**exp) - 1) * 100) if invested > 0 else 0
            cagr_list.append(cagr)

        self.portfolio['cagr'] = cagr_list

    def allocation_analysis(self):
        invested = self.shares * self.price
        equity = self.portfolio['equity']

        self.portfolio['initial_weight'] = invested / invested.sum()
        self.portfolio['current_weight'] = equity / equity.sum()

    def summarize_events(self):
        event_summary = []
        for ticker in self.ticker:
            dividends_df = self.dividends[['Date', ticker]].dropna()
            last_div_date, last_div_value = dividends_df.iloc[-1] if not dividends_df.empty else (None, 0)
            event_summary.append({
                'ticker': ticker,
                'last_dividend_date': last_div_date,
                'last_dividend_value': last_div_value
            })
        return pd.DataFrame(event_summary)


    # KPIs

    def current_equity(self):
        equity_kpi = self.portfolio['equity'].sum()
        return equity_kpi

    def calculate_absolute_return(self):
        price = self.price
        shares = self.shares
        dividends = self.portfolio['dividends'].sum()
        equity = self.portfolio['equity'].sum()

        invested = (shares * price).sum()

        abs_return = ((equity - invested + dividends) / invested) * 100
        return abs_return

    def calculate_cagr(self):
        shares = self.shares
        price = self.price
        dividends = self.portfolio['dividends'].sum()
        equity = self.portfolio['equity'].sum()
        invested = (shares * price).sum()

        min_date = self.acq_date.min()
        time_investing = dt.today() - dt.strptime(min_date, '%Y-%m-%d')
        portfolio_age = int(str(time_investing).split(' ')[0])

        exp = 365.25 / (portfolio_age)

        cagr = ((((equity + dividends)/invested)**exp) - 1) * 100

        return cagr

    def drawdown(self):
        shares = self.portfolio.set_index('ticker')['shares']

        weighted_df = self.prices.multiply(shares, axis=1).fillna(0)
        weighted_df['equity'] = weighted_df.sum(axis=1)
        weighted_df['max'] = weighted_df['equity'].cummax()
        weighted_df['dd'] = (weighted_df['equity'] - weighted_df['max']) / weighted_df['max']

        return weighted_df['dd'].min() * 100

    def build_wallet(self):
        self.current_price()
        self.calculate_equity()
        self.calculate_return()
        self.calculate_dividends()
        self.calculate_return_dividend()
        self.last_dividend()
        self.calculate_cagr_individual()
        self.allocation_analysis()

        self.current_equity()
        self.calculate_absolute_return()
        self.calculate_cagr()
        self.drawdown()

        return self.portfolio


wallet = Wallet()

test = wallet.build_wallet()
print(test)