import numpy as np
from pandas import DataFrame

def calculate_indicators(stock_data: DataFrame) -> DataFrame:
    if "Shares_Outstanding" in stock_data.columns:
        # Formula: Volume / Shares Outstanding
        stock_data['Turnover_Ratio'] = stock_data['Volume'] / stock_data['Shares_Outstanding'] * 100
    else: 
        # Approximate Formula: Volumn / closing price
        stock_data['Turnover_Ratio'] = stock_data['Volume'] / stock_data['Close'] * 100

    stock_data['ADTV_20'] = stock_data['Volume'].rolling(window=20).mean()
    return stock_data

def generate_signals(stock_data: DataFrame) -> DataFrame:
    # mean() is NAN-safe, ignores NAN
    # use standard deviations to identify extreme values
    turnover_mean = stock_data['Turnover_Ratio'].mean()
    turnover_std = stock_data['Turnover_Ratio'].std()
    adtv_mean = stock_data['ADTV_20'].mean()
    adtv_std = stock_data['ADTV_20'].std()
    turnover_high = turnover_mean + turnover_std
    turnover_low = turnover_mean - turnover_std
    adtv_high = adtv_mean + adtv_std
    adtv_low = adtv_mean - adtv_std

    stock_data['Buy_Signal'] = (stock_data['Turnover_Ratio'] > turnover_high) & (stock_data['ADTV_20'] > adtv_high)
    stock_data['Sell_Signal'] = (stock_data['Turnover_Ratio'] < turnover_low) & (stock_data['ADTV_20'] < adtv_low)

    stock_data['Buy_Description'] = np.where(
        stock_data['Buy_Signal'], 
        "Turnover Ratio and ADTV above average", 
        ""
    )

    stock_data['Sell_Description'] = np.where(
        stock_data['Sell_Signal'], 
        "Turnover Ratio and ADTV below average", 
        ""
    )
    
    return stock_data

def compute_liquidity_analysis(stock_data: DataFrame):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    result = result.to_dict()
    return result
