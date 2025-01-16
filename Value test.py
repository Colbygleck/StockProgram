import yfinance as yf

stock_symbol = 'ACGL'
ticker = yf.Ticker(stock_symbol)

# Get components to calculate enterprise value
market_cap = ticker.info.get('marketCap', 'N/A')
total_debt = ticker.info.get('totalDebt', 0)
cash_and_cash_equiv = ticker.info.get('totalCash', 0)

# Calculate enterprise value manually
if market_cap != 'N/A':
    enterprise_value = market_cap + total_debt - cash_and_cash_equiv
    print(f"Market Cap: ${market_cap/1e9:.2f}B")
    print(f"Total Debt: ${total_debt/1e9:.2f}B")
    print(f"Cash & Equivalents: ${cash_and_cash_equiv/1e9:.2f}B")
    print(f"Calculated Enterprise Value: ${enterprise_value/1e9:.2f}B")
    print(f"YFinance Direct EV: ${ticker.info.get('enterpriseValue', 'N/A')/1e9:.2f}B")
else:
    print("Could not calculate enterprise value - missing data")