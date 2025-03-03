from pandas import DataFrame
from fin_common.YfinanceService import yf_get_info
from fin_common.technical_anslysis.liquidity import compute_liquidity_analysis
from fin_common.technical_anslysis.pattern import compute_pattern_analysis
from fin_common.technical_anslysis.momentum import compute_momentum_analysis
from fin_common.technical_anslysis.volatility import compute_volatility_analysis
from fin_common.technical_anslysis.util import fetch_data

def perform_technical_analysis(ticker: str) -> DataFrame | None:
    # Perform technical analysis based on the analysis_type
    # and return the analysis result

    ## fetch relavant data for ticker
    stock_data = fetch_data(ticker)
    if stock_data is None:
        return None
    info = yf_get_info(ticker)
    if info is None:
        return None
    elif info['sharesOutstanding'] != None:
        stock_data['Shares_Outstanding'] = info['sharesOutstanding']

    ## Send stock data for analysis
    return {
        "volatility_analysis": compute_volatility_analysis(stock_data),
        "momentum_analysis": compute_momentum_analysis(stock_data),
        "pattern_analysis": compute_pattern_analysis(stock_data),
        "liquidity_analysis": compute_liquidity_analysis(stock_data)
    }
