import yfinance as yf
import pandas as pd
from fin_common.yfinance_service import yf_download_data

# short term goal: period = 1mo, interval = 1m, 5m, 15m, or 1h
# medium term goal: period = 6mo, interval = 1d
# long term goal: period = 1y, interval = 1wk, 1mo
short_period = '1mo'
medium_period = '6mo'
long_period = '1y'
short_interval = '1h'
medium_interval = '1d'
long_interval = '1wk'

def fetch_data(ticker):
    data = yf_download_data(ticker, period=short_period, interval=short_interval)
    if data is None:
        return None
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]  # Keep only the first level labels (e.g., 'Close', 'Open', not the tickers)
    return data