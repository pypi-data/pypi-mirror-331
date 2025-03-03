# ATR + Bollinger Bands + AD - Volatility analysis
import talib
import numpy as np
import pandas as pd
from pandas import DataFrame

def calculate_indicators(data: DataFrame) -> DataFrame:
    # Convert columns to numpy arrays
    high = data['High'].to_numpy().astype('float64').flatten()
    low = data['Low'].to_numpy().astype('float64').flatten()
    close = data['Close'].to_numpy().astype('float64').flatten()
    volume = data['Volume'].to_numpy().astype('float64').flatten()

    # Calculate ATR
    atr = pd.DataFrame(talib.ATR(high, low, close, timeperiod=14), index=data.index, columns=['ATR'])

    # Calculate Bollinger Bands
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=14, nbdevup=1.5, nbdevdn=1.5, matype=0)
    bb_upper = pd.DataFrame(upperband, index=data.index, columns=['BB_Upper'])
    bb_middle = pd.DataFrame(middleband, index=data.index, columns=['BB_Middle'])
    bb_lower = pd.DataFrame(lowerband, index=data.index, columns=['BB_Lower'])

    # Calculate Accumulation/Distribution Line (AD)
    ad = pd.DataFrame(talib.AD(high, low, close, volume), index=data.index, columns=['AD'])

    # Combine all indicators with the original DataFrame
    data = pd.concat([data, atr, bb_upper, bb_middle, bb_lower, ad], axis=1)

    data['BB_Lower'] = data['BB_Lower'].fillna(float('-inf'))
    data['BB_Upper'] = data['BB_Upper'].fillna(float('inf'))
    data['ATR_14'] = data['ATR'].rolling(window=14).mean().fillna(float('inf'))

    return data

def generate_signals(data: DataFrame) -> DataFrame:
    data['Buy_Signal'] = (
        (data['Close'] < data['BB_Lower']) &
        (data['ATR'] > 0.9 * data['ATR_14'])
    )

    data['Sell_Signal'] = (
        (data['Close'] > data['BB_Upper']) &
        (data['ATR'] > 0.9 * data['ATR_14'])
    )

    data['Buy_Description'] = np.where(
        data['Buy_Signal'], 
        "Close price below Bollinger Lower Band and ATR above 90% of 14-day ATR", 
        ""
    )

    data['Sell_Description'] = np.where(
        data['Sell_Signal'], 
        "Close price above Bollinger Upper Band and ATR above 90% of 14-day ATR", 
        ""
    )

    return data

# returns a dict
def compute_volatility_analysis(stock_data: DataFrame):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    result = result.to_dict()
    return result