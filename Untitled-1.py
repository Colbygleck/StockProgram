import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Parses numeric values like "1.5B", "2.3M", "1.2T" into float numbers
def parse_numeric_value(value):
    if isinstance(value, str):
        if "B" in value:
            return float(value.replace("B", "")) * 1e9
        elif "M" in value:
            return float(value.replace("M", "")) * 1e6
        elif "T" in value:
            return float(value.replace("T", "")) * 1e12
        else:
            return float(value.replace(",", ""))
    return value

# Scrapes the Enterprise Value from the Yahoo Finance financials page
def get_Enterprise_Value(ticker_symbol):
    url = f"https://finance.yahoo.com/quote/{ticker_symbol}/key-statistics"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.find_all('tr')
        for row in rows:
            if row.find(string='Enterprise Value'):
                # Extract the first 'td' containing the value
                ev_cell = row.find_all('td')[-1]  # Typically the last cell contains the value
                ev = ev_cell.text.strip() if ev_cell else None
                return parse_numeric_value(ev)
    except Exception as e:
        print(f"Error scraping EV for {ticker_symbol}: {e}")
    return None

# Pulls data from Yahoo Finance and uses the scraped EV
def pull_yahoo_data(ticker):
    try:
        ev = get_Enterprise_Value(ticker)
        
        stock = yf.Ticker(ticker)
        net_income = stock.info.get('netIncomeToCommon', 0)
        revenue = stock.financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in stock.financials.index else None
        ebitda = stock.financials.loc['EBITDA'].iloc[0] if 'EBITDA' in stock.financials.index else None
        total_debt = stock.info.get('totalDebt', 0)
        cash = stock.info.get('totalCash', 0)

        print(f"Ticker: {ticker}, Enterprise Value: {ev}, Net Income: {net_income}")

        return {
            'ticker': ticker,
            'enterprise_value': ev,  # Matches `web_ev`
            'revenue': revenue,
            'net_income': net_income,
            'ebitda': ebitda,
            'total_debt': total_debt,
            'cash': cash
        }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Calculates financial metrics
def calculate_metrics(data):
    try:
        enterprise_value = data['enterprise_value'] or 1  # Only using the scraped EV
        net_income = data['net_income'] or 0
        revenue = data['revenue'] or 1
        ebitda = data['ebitda'] or 1
        total_debt = data['total_debt'] or 0
        cash = data['cash'] or 0

        roe = net_income / enterprise_value
        net_debt_to_ebitda = (total_debt - cash) / ebitda if ebitda else None
        net_profit_margin = net_income / revenue
        p_e_ratio = enterprise_value / net_income if net_income != 0 else None

        return {
            'ticker': data['ticker'],
            'roe': roe,
            'net_debt_to_ebitda': net_debt_to_ebitda,
            'net_profit_margin': net_profit_margin,
            'p_e_ratio': p_e_ratio
        }
    except Exception as e:
        print(f"Error calculating metrics for {data['ticker']}: {e}")
        return None

# Displays results in a DataFrame
def display_results(results):
    df = pd.DataFrame(results)
    print(df.to_string(index=False))

# Main function to process multiple tickers
if __name__ == "__main__":
    tickers = ["ACGL"]
    all_results = []

    for ticker in tickers:
        data = pull_yahoo_data(ticker)
        if data:
            metrics = calculate_metrics(data)
            if metrics:
                all_results.append(metrics)

    display_results(all_results)
