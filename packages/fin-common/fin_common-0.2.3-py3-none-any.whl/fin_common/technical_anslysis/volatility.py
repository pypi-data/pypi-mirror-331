# ATR + Bollinger Bands + AD - Volatility analysis
import talib
import numpy as np
import pandas as pd
from pandas import DataFrame
from fin_common.llm_util import query_llm
from langchain_core.prompts import PromptTemplate

volatility_interpretation_template = """
You are a financial analysis assistant specializing in volatility analysis for stocks. 
Your goal is to simplify complex stock market indicators for beginner investors and provide clear, concise, and jargon-free interpretations of a stock's volatility. 
Explain what the data suggests about market trends, price movements, and potential risks/opportunities specific to the stock. 
Use analogies and simple explanations to make concepts easy to understand. 
Avoid use of markdown or anything similar (bold - **, highlight, etc.).

### Input Data:
- Stock Ticker
- Last Open/Close Price
- High/Low Price
- Volume
- ATR
- Bollinger Bands
- Accumulation/Distribution

### Guidelines:
- **Explain the meaning** of each key indicator in the context of the current stock.
- **Use simple terms and relatable analogies** (e.g., “The Bollinger Bands act like guardrails on a road…”).
- **Highlight key takeaways** for investors (e.g., “This suggests increased risk but also potential buying opportunities.”).
- **Be concise but insightful** (max 2-3 sentences).

### Example Response:
Apple's stock is experiencing **moderate volatility**, as seen in its **ATR of 2.5**, meaning its daily price swings are slightly above average. The stock recently **dipped near the lower Bollinger Band**, suggesting it might be **oversold**—like a rubber band stretching too far before snapping back. However, ATR remains high, signaling **uncertainty and increased risk**. If buying pressure (Accumulation/Distribution) rises, we could see a rebound, but caution is advised in volatile conditions."

Input: {input}
"""
prompt_template = PromptTemplate.from_template(volatility_interpretation_template)


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
def compute_volatility_analysis(ticker: str, stock_data: DataFrame, with_interpretation: bool):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    if with_interpretation:
        result['interpretation'] = query_llm(f"stock ticker: {ticker}, analysis result: {str(result)}", prompt_template)
    result = result.to_dict()
    return result