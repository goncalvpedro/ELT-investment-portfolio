from dash import Dash, html, dash_table, dcc
from middleware.transform import Wallet
import plotly.express as px


app = Dash()
wallet = Wallet()

portfolio_df = wallet.build_wallet()

dividends_df = wallet.dividends.fillna(0)
historic_prices = wallet.prices
normalized = wallet._price_return_vs_paid(historic_prices, portfolio_df)
portfolio_return = wallet.compute_portfolio_return(historic_prices, portfolio_df)


portfolio_df['weight_variation'] = round(
    100 * (portfolio_df['current_weight'] - portfolio_df['initial_weight']) / portfolio_df['initial_weight'], 3)
portfolio_df['current_price'] = round(portfolio_df['current_price'], 3)
portfolio_df['return_dividends'] = round(portfolio_df['return_dividends'], 3)
portfolio_df['cagr'] = round(portfolio_df['cagr'], 3)
portfolio_df['weight_variation'] = round(portfolio_df['weight_variation'], 3)
portfolio_df['current_weight'] = round(portfolio_df['current_weight'], 3)

formatted_df = portfolio_df[['ticker', 'current_price',
                             'return_dividends', 'cagr', 'current_weight', 'weight_variation']].rename(columns={'ticker': 'Symbol', 'current_price': 'Current Price (USD)', 'return_dividends': 'Return with Dividends (%)', 'cagr': 'CAGR (%)', 'current_weight': 'Allocation (%)', 'weight_variation': 'Allocation variation (%)'})

app.layout = [
    html.H1(children='Investments Dashboard'),
    html.Hr(),
    html.H2(children='Wallet'),
    dash_table.DataTable(data=formatted_df.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.line(data_frame=normalized, x=normalized.index, y=normalized.columns))
]

if __name__ == '__main__':
    app.run(debug=True)
