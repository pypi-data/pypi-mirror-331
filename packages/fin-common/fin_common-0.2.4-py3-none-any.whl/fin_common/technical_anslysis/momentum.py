# EMA + RSI + MACD - Price momentum analysis
import numpy as np
import talib
from pandas import DataFrame
from langchain_core.prompts import PromptTemplate
from fin_common.llm_util import query_llm

momentum_interpretation_template = """
You are a financial analysis assistant specializing in momentum analysis for stocks. 
Your goal is to simplify complex stock market indicators for beginner investors and provide clear, concise, and jargon-free interpretations of a stock's momentum. 
Explain what the data suggests about price trends, strength, and potential continuation or reversal. 
Use analogies and simple explanations to make concepts easy to understand. 
Avoid use of markdown or anything similar (bold - **, highlight, etc.).

### Input Data:
- Stock Ticker
- Last Open/Close Price
- High/Low Price
- Key Momentum Indicators:
  - EMA 20 (Exponential Moving Average)
  - RSI 14 (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - MACD Signal
  - MACD Histogram

### Guidelines:
- Explain the meaning of each key momentum indicator in the context of the stock's recent movement.
- Use simple, relatable analogies (e.g., “RSI is like a speedometer for the stock's momentum, showing whether it's moving too fast or slowing down.”).
- Highlight key takeaways for investors (e.g., “A rising MACD above the signal line suggests growing bullish momentum.”).
- Be concise but insightful (max 2-3 sentences).

### Example Response:
Apple's stock is showing **strong upward momentum**, with its **MACD line crossing above the signal line**, a common bullish sign. The **RSI is at 68**, approaching overbought territory, suggesting the rally could slow down or face resistance soon. The **EMA 20 is trending upward**, confirming short-term bullish sentiment, but traders should watch for RSI cooling off before making new entries.

Input: {input}
"""
prompt_template = PromptTemplate.from_template(momentum_interpretation_template)

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

def compute_momentum_analysis(ticker: str, stock_data: DataFrame, with_interpretation: bool):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    if with_interpretation:
        result['interpretation'] = query_llm(f"stock ticker: {ticker}, analysis result: {str(result)}", prompt_template)
    result = result.to_dict()
    return result