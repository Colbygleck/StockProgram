import yfinance as yf

stock_symbol = 'ACGL'

ticker = yf.Ticker(stock_symbol)

stock_data = ticker.history(period='5d', interval='1h',)

financials = ticker.financials

enterprise_value = ticker.info.get('enterpriseValue', 'N/A')
net_income = financials.loc['Net Income'] if 'Net Income' in financials.index else 'N/A'

print("Stock Data (Last 5 days, 1 hour interval):")
print(stock_data)
print("\nEnterprise Value:", enterprise_value)
print("Net Income:", net_income)