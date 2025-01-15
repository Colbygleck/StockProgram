
#Code in progress 
import os 
import yfinance as yf
import pandas as pd 
import tkinter as tk
from tkinter import ttk

#Function to fetch stock data
def fetch_data(tickers):
    data = {}
    financials = {}
    for ticker in tickers:
        try:
            ticker_data = yf.download(ticker, period='1d', interval='1m', group_by='ticker')
            ticker_financials = yf.Ticker(ticker).financials
            if not ticker_data.empty and not ticker_financials.empty:
                data[ticker] = ticker_data
                financials[ticker] = ticker_financials
                print(f"Fetched data for {ticker}")

            else:
                print(f"{ticker}: No data found")
        except Exception as e:
            print(f"{ticker}: {e}")
    return data, financials

#Function to process stock data

def process_data(data, financials):
    metrics = []
    for ticker in financials:
        stock_financials = financials[ticker]
        try:
            revenue_2023 = stock_financials.loc['Total Revenue', '2023']
            revenue_2022 = stock_financials.loc['Total Revenue', '2022']
            net_income_ttm = stock_financials.loc['Net Income', '2023']
            revenue_ttm = stock_financials.loc['Total Revenue', '2023']
            enterprise_value = yf.Ticker(ticker).info.get('enterpriseValue', None)

            #Handle cases where data may be missing
            revenue_2023 = revenue_2023.iloc[0] if isinstance(revenue_2023, pd.Series) else revenue_2023
            revenue_2022 = revenue_2022.iloc[0] if isinstance(revenue_2022, pd.Series) else revenue_2022
            net_income_ttm =net_income_ttm.iloc[0] if isinstance(net_income_ttm, pd.Series) else net_income_ttm
            revenue_ttm = revenue_ttm.iloc[0] if isinstance(revenue_ttm, pd.Series) else revenue_ttm

            if enterprise_value is None:
                print(f"{ticker}: Enterprise value is missing")
                continue #Skip if enterprise value is missing

            enterprise_value = float(enterprise_value)

            roev = (net_income_ttm / enterprise_value) * 100
            annual_change_revenue = (((revenue_2023 / revenue_2022) - 1) /2) * 100
            net_profit_margin = (net_income_ttm / revenue_ttm) * 100

            metrics.append((ticker, roev, annual_change_revenue, net_profit_margin))
        except KeyError as e:
            print(f"{ticker}: Missing financial data for {e}")
        except Exception as e:
            print(f"{ticker}: Error processing data - {e}")

    return pd.DataFrame(metrics, columns=['Ticker', 'RoEV (%)', 'Annual Change in Revenue (%)', 'Net Profit Margin (%)'])

# Function to display metrics in a new window
def display_metrics(df):
    root = tk.Tk()
    root.title("Stock Metrics")
    
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    tree = ttk.Treeview(frame, columns=tuple(df.columns), show='headings')
    tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    
    for index, row in df.iterrows():
        tree.insert("", "end", values=tuple(row))
    
    root.mainloop()

# Main function to fetch, process, display, and save data
def main():
    tickers = ['JBL']
    data, financials = fetch_data(tickers)
    df = process_data(data, financials)
    
    if df.empty:
        print("No data to display or save.")
    else:
        display_metrics(df)

if __name__ == "__main__":
    main()