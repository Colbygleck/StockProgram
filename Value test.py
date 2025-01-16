import yfinance as yf
import requests
from bs4 import BeautifulSoup

def get_yahoo_statistics(ticker_symbol):
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
               
       return ev, net_income
   except Exception as e:
       return f"Error: {e}", f"Error: {e}"

stock_symbol = 'ACGL'
ticker = yf.Ticker(stock_symbol)

# Get values from Yahoo Finance website
web_ev, web_net_income = get_yahoo_statistics(stock_symbol)
print(f"Yahoo Finance Website EV: ${web_ev}")

# Calculate EV using yfinance data
market_cap = ticker.info.get('marketCap', 'N/A')
total_debt = ticker.info.get('totalDebt', 0)
cash_and_cash_equiv = ticker.info.get('totalCash', 0)

if market_cap != 'N/A':
   ev_calculated = market_cap + total_debt - cash_and_cash_equiv
   print(f"YFinance Calculated EV: ${ev_calculated/1e9:.2f}B")
   print(f"YFinance Direct EV: ${ticker.info.get('enterpriseValue', 'N/A')/1e9:.2f}B")
   print(f"YFinance Net Income: ${ticker.info.get('netIncomeToCommon', 0)/1e9:.2f}B")