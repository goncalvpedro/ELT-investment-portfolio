````markdown
# Portfolio Dividends Dashboard

![Dashboard Preview](assets/dashboard-screenshot.png)

An interactive **Portfolio Dividends Dashboard** built with Dash and Plotly to visualize dividends received, portfolio performance, and monthly top gainers and losers based on prices. Powered by a custom Python `Wallet` class for managing and processing your financial data.

---

## Features

- 📊 **Monthly Dividends Bar Chart:** Displays total dividends received, proportional to shares held and acquisition dates.
- 📋 **Portfolio Overview Table:** Shows key portfolio metrics like returns, dividends, and CAGR, with values rounded to 3 decimals.
- 🚀 **Top 3 Gainers and Losers Table:** Highlights the biggest movers in your portfolio over the current month based on price changes.
- 📈 **Portfolio KPIs:** Current portfolio value, CAGR, maximum drawdown.
- 🎨 Responsive and polished UI using Dash Bootstrap Components for a clean, modern look.

---

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/finance-dividends-dashboard.git
   cd finance-dividends-dashboard
````

2. (Optional but recommended) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Make sure your data files (`portfolio.json`, `dividends.csv`, `prices.csv`) are placed correctly in the project structure.

---

## Usage

Run the dashboard locally:

```bash
python app.py
```

Then open your browser to `http://127.0.0.1:8050/` to view the dashboard.

---

## Project Structure

```
finance-dividends-dashboard/
├── app.py               # Main dashboard application
├── Wallet.py            # Wallet class managing portfolio and calculations
├── output/
│   ├── dividends.csv    # Dividends data file
│   └── prices.csv       # Prices data file
├── portfolio.json       # Portfolio data file
├── requirements.txt     # Python dependencies
├── assets/              # Optional images and styling assets
└── README.md            # This file
```

---

## Dependencies

* Python 3.7+
* [Dash](https://dash.plotly.com/)
* [Plotly](https://plotly.com/python/)
* [pandas](https://pandas.pydata.org/)
* [dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/)

---

## Screenshots

![Dashboard Screenshot](assets/dashboard-screenshot.png)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Feel free to submit issues and pull requests. Contributions are very welcome!

---

## Contact

Created by **Your Name**. Connect with me:

* [LinkedIn](https://www.linkedin.com/in/yourprofile)
* [Twitter](https://twitter.com/yourhandle)

---


```
