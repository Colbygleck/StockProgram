import os
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Parse numeric values like "1.5B", "2.3M", etc.
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

def format_large_number(value):
    try:
        value = float(value)
        if value >= 1e12:
            return f"{value / 1e12:.2f}T"  # Trillions
        elif value >= 1e9:
            return f"{value / 1e9:.2f}B"  # Billions
        elif value >= 1e6:
            return f"{value / 1e6:.2f}M"  # Millions
        else:
            return f"{value:.2f}"  # Less than a million
    except (ValueError, TypeError):
        return "N/A"

# Scrapes the Enterprise Value off Yahoo Finance
def scrape_yahoo_statistics(ticker_symbol):
    url = f"https://finance.yahoo.com/quote/{ticker_symbol}/key-statistics"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.find_all('tr')
        ev = None
        
        for row in rows:
            if row.find(string='Enterprise Value'):
                ev = row.find_all('td')[1].text.strip()
                break
        
        return ev
    except Exception as e:
        return f"Error: {e}"

# Pull Yahoo Statistics for net income
def pull_yahoo_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        net_income = stock.info.get('netIncomeToCommon', 0)
        return str(net_income)  # Return as a string for parsing
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Calculate Return on Enterprise Value
def calculate_roev(ev, net_income):
    try:
        ev_value = parse_numeric_value(ev)
        net_income_value = parse_numeric_value(net_income)

        if ev_value > 0:
            roev = (net_income_value / ev_value) * 100
            return roev
        else:
            return "Enterprise Value must be greater than 0"
    except Exception as e:
        return f"Error in calculation: {e}"

# Process multiple stock symbols
def process_stocks(stock_symbols):
    results = []

    for stock_symbol in stock_symbols:
        print(f"Processing {stock_symbol}...")
        
        ev = scrape_yahoo_statistics(stock_symbol)
        net_income = pull_yahoo_data(stock_symbol)
        
        if ev and net_income:
            roev_result = calculate_roev(ev, net_income)
            results.append({
                'Ticker': stock_symbol,
                'Enterprise Value': format_large_number(parse_numeric_value(ev)),
                'Net Income': format_large_number(parse_numeric_value(net_income)),
                'RoEV (%)': roev_result if isinstance(roev_result, float) else "N/A"
            })
        else:
            results.append({
                'Ticker': stock_symbol,
                'Enterprise Value': "N/A",
                'Net Income': "N/A",
                'RoEV (%)': "N/A"
            })
    
    return pd.DataFrame(results)


# List of stock symbols to process
stock_symbols = ['IONQ', 'GOOG', 'UBER', 'RDDT', 'IBM', 'INTC', 'ZS', 'NET', 'DDOG']
results_df = process_stocks(stock_symbols)

# Display results
print(results_df)

# Save results to a CSV file
results_df.to_csv("stock_roev_results.csv", index=False)
print("Results saved to stock_roev_results.csv")
