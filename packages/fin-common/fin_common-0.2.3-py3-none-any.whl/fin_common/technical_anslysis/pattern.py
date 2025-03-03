# ADX + Candlestick Pattern - Trend direction analysis, Pattern Recognition

import talib
import numpy as np
from pandas import DataFrame
from fin_common.llm_util import query_llm
from langchain_core.prompts import PromptTemplate

pattern_interpretation_template = """
You are a financial analysis assistant specializing in pattern analysis for stocks. 
Your goal is to simplify complex stock market indicators for beginner investors and provide clear, concise, and jargon-free interpretations of candlestick patterns and trend indicators. 
Explain what the data suggests about potential price reversals, trend strength, and market direction specific to the stock. 
Use analogies and simple explanations to make concepts easy to understand. 
Avoid use of markdown or anything similar (bold - **, highlight, etc.).

### Input Data:
- Stock Ticker
- Last Open/Close Price
- High/Low Price
- ADX (Trend Strength)
- Candlestick Patterns:
  - Hammer
  - Engulfing
  - Shooting Star
  - Doji
  - Morning Star
  - Piercing
  - Takuri
- Directional Indicators:
  - Plus DI
  - Minus DI

### Guidelines:
- Explain the significance of detected candlestick patterns and whether they indicate a potential **trend reversal or continuation**.
- Use simple, relatable analogies (e.g., "A Doji is like a pause in a conversation, signaling market indecision.").
- Highlight key takeaways for investors (e.g., "A Morning Star pattern suggests a potential upward reversal after a downtrend.").
- Be concise but insightful (max 2-3 sentences).

### Example Response:
Apple's stock is showing **bullish reversal signals** with a **Morning Star pattern**, which often indicates a potential upward trend after a decline. The **ADX value of 25** suggests the current trend is gaining strength, confirming that momentum is shifting. However, the **presence of a Doji** also signals market hesitation, meaning traders may wait for further confirmation before making moves.

Input: {input}
"""
prompt_template = PromptTemplate.from_template(pattern_interpretation_template)

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

def compute_pattern_analysis(ticker: str, stock_data: DataFrame, with_interpretation: bool):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    if with_interpretation:
        result['interpretation'] = query_llm(f"stock ticker: {ticker}, analysis result: {str(result)}", prompt_template)
    result = result.to_dict()
    return result
