import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime
from middleware.transform import Wallet

# Initialize wallet and build portfolio
wallet = Wallet()
wallet.build_wallet()

# Round portfolio numeric columns to 3 decimals
portfolio_df = wallet.portfolio.round(3)

# Calculate KPIs
current_value = round(wallet.current_equity(), 2)
portfolio_cagr = round(wallet.calculate_cagr(), 2)
max_drawdown = round(wallet.drawdown(), 2)

# Prepare dividends DataFrame
dividends_df = wallet.dividends.copy()
dividends_df['Date'] = pd.to_datetime(dividends_df['Date'], utc=True, errors='coerce')
dividends_df = dividends_df.set_index('Date')

# Dictionary for ticker → shares
shares_dict = dict(zip(wallet.portfolio['ticker'], wallet.portfolio['shares']))

# Filter dividends by acquisition date per ticker, multiply by shares
filtered_divs = pd.DataFrame()

for _, row in wallet.portfolio.iterrows():
    ticker = row['ticker']
    acq_date = pd.to_datetime(row['first_acquisition'], utc=True)
    shares = row['shares']

    if ticker in dividends_df.columns:
        ticker_divs = dividends_df.loc[dividends_df.index >= acq_date, [ticker]].copy()
        ticker_divs[ticker] = ticker_divs[ticker].fillna(0) * shares
        filtered_divs = pd.concat([filtered_divs, ticker_divs], axis=1)

filtered_divs = filtered_divs.fillna(0)
filtered_divs['Total'] = filtered_divs.sum(axis=1)

monthly_dividends = filtered_divs[['Total']].resample('ME').sum().reset_index()
monthly_dividends.columns = ['Month', 'Total Dividends']

# Create bar chart for dividends
div_bar_fig = px.bar(
    monthly_dividends,
    x='Month',
    y='Total Dividends',
    title="Monthly Dividends Received",
    labels={'Month': 'Month', 'Total Dividends': 'Dividends ($)'},
    text_auto='.2s',
    color_discrete_sequence=['#007bff']
)
div_bar_fig.update_layout(
    plot_bgcolor='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor='lightgrey')
)

# === New: Calculate top gainers and losers for current month ===

prices_df = wallet.prices.copy()
prices_df['Date'] = pd.to_datetime(prices_df['Date'], utc=True)
prices_df = prices_df.set_index('Date').sort_index()

# Filter prices for current month
now = datetime.now()
current_month_start = pd.Timestamp(year=now.year, month=now.month, day=1, tz='UTC')

month_prices = prices_df.loc[prices_df.index >= current_month_start]

# Calculate pct change from first to last day of current month for each ticker
if not month_prices.empty:
    first_day_prices = month_prices.iloc[0]
    last_day_prices = month_prices.iloc[-1]
    pct_changes = ((last_day_prices - first_day_prices) / first_day_prices) * 100
    pct_changes = pct_changes.dropna()

    # Remove 'equity', 'max', 'dd' columns if present
    pct_changes = pct_changes[~pct_changes.index.isin(['equity', 'max', 'dd'])]

    # Get top 3 gainers and top 3 losers
    top_gainers = pct_changes.sort_values(ascending=False).head(3)
    top_losers = pct_changes.sort_values().head(3)

    # Prepare DataFrames for display
    top_gainers_df = top_gainers.reset_index()
    top_gainers_df.columns = ['Ticker', 'Change (%)']
    top_gainers_df['Change (%)'] = top_gainers_df['Change (%)'].round(2)

    top_losers_df = top_losers.reset_index()
    top_losers_df.columns = ['Ticker', 'Change (%)']
    top_losers_df['Change (%)'] = top_losers_df['Change (%)'].round(2)
else:
    # Fallback empty DataFrames
    top_gainers_df = pd.DataFrame(columns=['Ticker', 'Change (%)'])
    top_losers_df = pd.DataFrame(columns=['Ticker', 'Change (%)'])

# Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Enhanced Dividends Dashboard"

# KPI card helper
def kpi_card(title, value, color='primary'):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className='card-title text-muted'),
            html.H3(f"{value:,}", className=f'text-{color}')
        ]),
        className='shadow-sm p-3 mb-4 bg-white rounded text-center'
    )

app.layout = dbc.Container([
    html.H1("💸 Portfolio Dividends Dashboard", className='text-center my-4 mb-5'),

    dbc.Row([
        dbc.Col(kpi_card("Current Portfolio Value ($)", current_value, 'success'), md=4),
        dbc.Col(kpi_card("Portfolio CAGR (%)", portfolio_cagr, 'info'), md=4),
        dbc.Col(kpi_card("Max Drawdown (%)", max_drawdown, 'danger'), md=4),
    ], className='mb-5'),

    dbc.Row([
        dbc.Col([
            html.H4("Portfolio Overview", className='mb-3'),
            dash_table.DataTable(
                columns=[
                    {"name": i.capitalize(), "id": i}
                    for i in ['ticker', 'return', 'dividends', 'return_dividends', 'cagr']
                    if i in portfolio_df.columns
                ],
                data=portfolio_df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '10px', 'font-family': 'Segoe UI'},
                style_header={'backgroundColor': '#007bff', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
                    {'if': {'state': 'active'}, 'backgroundColor': '#D6EAF8', 'border': 'none'},
                ],
                page_size=15,
            ),
        ], md=12),
    ], className='mb-5'),

    # New row for top gainers and losers side by side
    dbc.Row([
        dbc.Col([
            html.H5(f"Top 3 Gainers - {now.strftime('%B %Y')}", className='mb-3'),
            dash_table.DataTable(
                data=top_gainers_df.to_dict('records'),
                columns=[{"name": c, "id": c} for c in top_gainers_df.columns],
                style_cell={'textAlign': 'center', 'font-family': 'Segoe UI'},
                style_header={'backgroundColor': '#28a745', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#eaf9ea'}
                ],
                page_size=3,
                style_table={'overflowX': 'auto'}
            ),
        ], md=6),

        dbc.Col([
            html.H5(f"Top 3 Losers - {now.strftime('%B %Y')}", className='mb-3'),
            dash_table.DataTable(
                data=top_losers_df.to_dict('records'),
                columns=[{"name": c, "id": c} for c in top_losers_df.columns],
                style_cell={'textAlign': 'center', 'font-family': 'Segoe UI'},
                style_header={'backgroundColor': '#dc3545', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9eaea'}
                ],
                page_size=3,
                style_table={'overflowX': 'auto'}
            ),
        ], md=6),
    ], className='mb-5'),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=div_bar_fig)
        ], md=12)
    ]),

], fluid=True, style={'maxWidth': '1100px'})


if __name__ == '__main__':
    app.run(debug=True)
