import numpy as np
from pandas import DataFrame
from langchain_core.prompts import PromptTemplate
from fin_common.llm_util import query_llm

liquidity_interpretation_template = """
You are a financial analysis assistant specializing in liquidity analysis for stocks. 
Your goal is to simplify complex stock market liquidity indicators for beginner investors and provide clear, concise, and jargon-free interpretations of a stock's liquidity. 
Explain what the data suggests about how easily the stock can be bought or sold, potential price stability, and investor interest. 
Use analogies and simple explanations to make concepts easy to understand. 
Avoid use of markdown or anything similar (bold - **, highlight, etc.).

### Input Data:
- Stock Ticker
- Last Open/Close Price
- High/Low Price
- Turnover Ratio (Liquidity measure)
- ADTV 20 (Average Daily Trading Volume over 20 days)

### Guidelines:
- Explain the significance of turnover ratio and ADTV in the context of liquidity.
- Use simple, relatable analogies (e.g., "Liquidity is like a busy marketplace - the more people buying and selling, the easier it is to trade at stable prices.").
- Highlight key takeaways for investors (e.g., "A low turnover ratio may indicate lower investor interest, leading to price volatility when large trades occur.").
- Be concise but insightful (max 2-3 sentences).

### Example Response:
Apple's stock is showing **high liquidity**, with an **ADTV of 50 million shares**, meaning it is actively traded and easy to buy or sell without large price swings. The **turnover ratio is at 1.2%**, indicating steady investor participation but not excessive speculation. This suggests that Apple’s stock is in a stable trading environment where orders can be filled efficiently without major price fluctuations.
Input: {input}
"""
prompt_template = PromptTemplate.from_template(liquidity_interpretation_template)


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

def compute_liquidity_analysis(ticker: str, stock_data: DataFrame, with_interpretation: bool):
    stock_data = calculate_indicators(stock_data)
    stock_data = generate_signals(stock_data)
    result = stock_data.iloc[-1]  # Get the most recent data point, which is a pandas Series (1d numpy array)
    if with_interpretation:
        result['interpretation'] = query_llm(f"stock ticker: {ticker}, analysis result: {str(result)}", prompt_template)
    result = result.to_dict()
    return result
