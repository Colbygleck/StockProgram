import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

## Parses numeric values like "1.5B", "2.3M", "1.2T" into float numbers
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
#Scrapes the Enterprise Value off Yahoo Finance and stores the variable as ev
def scrape_yahoo_statistics(ticker_symbol):
   url = f"https://finance.yahoo.com/quote/{ticker_symbol}/key-statistics"
   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
   
   try:
       response = requests.get(url, headers=headers)
       soup = BeautifulSoup(response.text, 'html.parser')
       
       # Find all table rows
       rows = soup.find_all('tr')
       
       ev = None
       net_income = None
       
       # Look for both Enterprise Value and Net Income
       for row in rows:
           if row.find(string='Enterprise Value'):
               ev = row.find_all('td')[1].text.strip()
               
       return ev,
   except Exception as e:
       return f"Error: {e}"

#Pull Yahoo Statistics 
def pull_yahoo_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        net_income = stock.info.get('netIncomeToCommon', 0)
        return {
            'ticker': ticker,
            'net_income': net_income,
        }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None




stock_symbol = 'ACGL'
ticker = yf.Ticker(stock_symbol)


web_ev = scrape_yahoo_statistics(stock_symbol)
print(f"Yahoo Finance Website EV: ${web_ev}")
net_income_data = pull_yahoo_data(stock_symbol)
if net_income_data and 'net_income' in net_income_data:
    print(f"Net Income: ${net_income_data['net_income']}")
else:
    print("Net Income data not availible.")