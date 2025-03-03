# EMA + RSI + MACD - Price momentum analysis
import numpy as np
import talib
from pandas import DataFrame

def calculate_indicators(data: DataFrame) -> DataFrame:
    close = data['Close'].to_numpy().astype('float64').flatten()
    data['EMA_20'] = talib.EMA(close, timeperiod=20)
    data['RSI_14'] = talib.RSI(close, timeperiod=14)
    macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    data['MACD'] = macd
    data['MACD_Signal'] = macd_signal
    data['MACD_Hist'] = macd_hist
    return data

def generate_signals(data) -> DataFrame:
    data['Buy_Signal'] = (
        (data['RSI_14'] < 40) &
        (data['MACD'] > data['MACD_Signal'])
    )

    data['Sell_Signal'] = (
        (data['RSI_14'] > 70) &
        (data['MACD'] < data['MACD_Signal'])
    )

    data['Buy_Description'] = np.where(
        data['Buy_Signal'], 
        "RSI below 40 and MACD above MACD Signal", 
        ""
    )

    data['Sell_Description'] = np.where(
        data['Sell_Signal'], 
        "RSI above 70 and MACD below MACD Signal", 
        ""
    )

    return data

def compute_momentum_analysis(stock_data: DataFrame):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    result = result.to_dict()
    return result