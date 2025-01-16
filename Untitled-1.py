import pandas as pd
import yfinance as yf
import tkinter as tk
from tkinter import ttk
from typing import Dict, Tuple, Optional, List
import numpy as np

def fetch_enterprise_value(ticker: str) -> Optional[float]:
    """Fetch enterprise value for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('enterpriseValue')
    except Exception as e:
        print(f"{ticker}: Error fetching enterprise value - {e}")
        return None

def fetch_net_debt_and_ebitda(ticker: str, financials: pd.DataFrame) -> Optional[float]:
    """Calculate Net Debt/EBITDA ratio."""
    try:
        # Get the most recent year's data
        latest_year = financials.columns[0]
        
        total_debt = financials.get('Total Debt', pd.Series()).get(latest_year)
        cash = financials.get('Cash and Cash Equivalents', pd.Series()).get(latest_year)
        ebitda = financials.get('EBITDA', pd.Series()).get(latest_year)
        
        if any(v is None for v in [total_debt, cash, ebitda]):
            print(f"{ticker}: Missing debt, cash, or EBITDA data")
            return None
            
        if ebitda == 0:
            return None
            
        net_debt = total_debt - cash
        return net_debt / ebitda
    except Exception as e:
        print(f"{ticker}: Error calculating Net Debt/EBITDA - {e}")
        return None

def fetch_data(tickers: List[str]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """Fetch price and financial data for given tickers."""
    data = {}
    financials = {}
    
    for ticker in tickers:
        try:
            # Fetch price data
            price_data = yf.download(ticker, period='1d', interval='1m', group_by='ticker', progress=False)
            if not price_data.empty:
                data[ticker] = price_data
            
            # Fetch financial data
            stock = yf.Ticker(ticker)
            financial_data = stock.financials
            if not financial_data.empty:
                financials[ticker] = financial_data
            
        except Exception as e:
            print(f"{ticker}: Error fetching data - {e}")
            
    return data, financials

def fetch_pe_ratio(ticker: str) -> Optional[float]:
    """Fetch P/E ratio for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        price = stock.info.get('currentPrice')
        eps = stock.info.get('trailingEps')
        
        if price and eps and eps != 0:
            return price / eps
        return None
    except Exception as e:
        print(f"{ticker}: Error fetching P/E ratio - {e}")
        return None

def calculate_metrics(financials: pd.DataFrame, ticker: str) -> Optional[tuple]:
    """Calculate financial metrics for a given ticker."""
    try:
        latest_year = financials.columns[0]
        prev_year = financials.columns[1]
        
        # Extract required financial data
        revenue_current = financials.get('Total Revenue', pd.Series()).get(latest_year)
        revenue_prev = financials.get('Total Revenue', pd.Series()).get(prev_year)
        net_income = financials.get('Net Income', pd.Series()).get(latest_year)
        
        if any(v is None for v in [revenue_current, revenue_prev, net_income]):
            print(f"{ticker}: Missing required financial data")
            return None
            
        # Calculate metrics
        enterprise_value = fetch_enterprise_value(ticker)
        if not enterprise_value:
            return None
            
        roev = (net_income / enterprise_value) * 100 if enterprise_value != 0 else None
        revenue_growth = ((revenue_current / revenue_prev - 1) * 100) if revenue_prev != 0 else None
        profit_margin = (net_income / revenue_current * 100) if revenue_current != 0 else None
        net_debt_to_ebitda = fetch_net_debt_and_ebitda(ticker, financials)
        pe_ratio = fetch_pe_ratio(ticker)
        
        return (
            ticker,
            round(roev, 2) if roev is not None else None,
            round(revenue_growth, 2) if revenue_growth is not None else None,
            round(profit_margin, 2) if profit_margin is not None else None,
            round(net_debt_to_ebitda, 2) if net_debt_to_ebitda is not None else None,
            round(pe_ratio, 2) if pe_ratio is not None else None
        )
    except Exception as e:
        print(f"{ticker}: Error calculating metrics - {e}")
        return None

def process_data(price_data: Dict[str, pd.DataFrame], financials: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Process data and create metrics DataFrame."""
    metrics = []
    for ticker, financial_data in financials.items():
        result = calculate_metrics(financial_data, ticker)
        if result:
            metrics.append(result)
    
    return pd.DataFrame(
        metrics,
        columns=[
            'Ticker',
            'RoEV (%)',
            'Annual Revenue Growth (%)',
            'Net Profit Margin (%)',
            'Net Debt/EBITDA',
            'P/E Ratio'
        ]
    )

def create_gui(df: pd.DataFrame) -> None:
    """Create and display GUI with metrics."""
    root = tk.Tk()
    root.title("Stock Metrics Analysis")
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create main frame
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky="nsew")
    
    # Create treeview
    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings')
    tree.grid(row=0, column=0, sticky="nsew")
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Configure columns
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")
    
    # Add data
    for _, row in df.iterrows():
        tree.insert("", "end", values=tuple(row))
    
    # Configure grid weights
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    root.mainloop()

def main():
    """Main function to run the program."""
    # Add your tickers here
    tickers = ['ACGL', 'AAPL', 'MSFT']  # Example tickers
    
    print("Fetching data...")
    price_data, financials = fetch_data(tickers)
    
    if not financials:
        print("No financial data available.")
        return
        
    print("Processing data...")
    df = process_data(price_data, financials)
    
    if df.empty:
        print("No data to display.")
        return
        
    print("Displaying results...")
    create_gui(df)

if __name__ == "__main__":
    main()