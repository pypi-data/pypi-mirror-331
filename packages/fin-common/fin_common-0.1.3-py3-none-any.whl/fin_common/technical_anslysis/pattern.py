# ADX + Candlestick Pattern - Trend direction analysis, Pattern Recognition

import talib
import numpy as np
from pandas import DataFrame

def calculate_indicators(data: DataFrame) -> DataFrame:
    high = data['High'].to_numpy().astype('float64').flatten()
    low = data['Low'].to_numpy().astype('float64').flatten()
    close = data['Close'].to_numpy().astype('float64').flatten()
    open = data['Open'].to_numpy().astype('float64').flatten()

    # Trend Strength Indicator (ADX)
    data['ADX'] = talib.ADX(high, low, close, timeperiod=14)

    # Candlestick Pattern Indicators
    data['Hammer'] = talib.CDLHAMMER(open, high, low, close)
    data['Engulfing'] = talib.CDLENGULFING(open, high, low, close)
    data['ShootingStar'] = talib.CDLSHOOTINGSTAR(open, high, low, close)
    data['Doji'] = talib.CDLDOJI(open, high, low, close)
    data['MorningStar'] = talib.CDLMORNINGSTAR(open, high, low, close)
    data['Piercing'] = talib.CDLPIERCING(open, high, low, close)
    data['Takuri'] = talib.CDLTAKURI(open, high, low, close)

    # Directional Indicators (+DI and -DI)
    data['PLUS_DI'] = talib.PLUS_DI(high, low, close, timeperiod=14)
    data['MINUS_DI'] = talib.MINUS_DI(high, low, close, timeperiod=14)
    
    return data

def generate_signals(data: DataFrame) -> DataFrame:
    data['Buy_Signal'] = (
        ((data['Hammer'] > 0) | (data['Engulfing'] > 0) | 
        (data['MorningStar'] > 0) | (data['Piercing'] > 0) | 
        (data['Takuri'] > 0)) &
        (data['ADX'] > 20) &
        (data['PLUS_DI'] > data['MINUS_DI'])
    )

    data['Sell_Signal'] = (
        ((data['ShootingStar'] < 0) | 
        (data['Engulfing'] < 0) | 
        (data['Doji'] < 0)) &
        (data['ADX'] > 20) &
        (data['MINUS_DI'] > data['PLUS_DI'])
    )
    data['Buy_Description'] = np.where(
        data['Buy_Signal'], 
        "Bullish candlestick pattern detected with strong trend (ADX > 20) and positive directional movement (PLUS_DI > MINUS_DI).", 
        ""
    )

    data['Sell_Description'] = np.where(
        data['Sell_Signal'], 
        "Bearish candlestick pattern detected with strong trend (ADX > 20) and negative directional movement (MINUS_DI > PLUS_DI).", 
        ""
    )

    return data

def compute_pattern_analysis(stock_data: DataFrame):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    result = result.to_dict()
    return result
