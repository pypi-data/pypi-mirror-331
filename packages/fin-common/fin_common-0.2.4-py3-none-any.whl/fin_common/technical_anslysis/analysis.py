from fin_common.yfinance_service import yf_get_info
from fin_common.technical_anslysis.liquidity import compute_liquidity_analysis
from fin_common.technical_anslysis.pattern import compute_pattern_analysis
from fin_common.technical_anslysis.momentum import compute_momentum_analysis
from fin_common.technical_anslysis.volatility import compute_volatility_analysis
from fin_common.technical_anslysis.util import fetch_data
from fin_common.technical_anslysis.analysis_type import AnalysisType
from datetime import datetime

def perform_technical_analysis(ticker: str, analysis_type: AnalysisType, with_interpretation: bool):
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
    # TODO: add more technical analysis combinations
    if analysis_type == AnalysisType.VOLATILITY:
        return compute_volatility_analysis(ticker, stock_data, with_interpretation)
    elif analysis_type == AnalysisType.MOMENTUM:
        return compute_momentum_analysis(ticker, stock_data, with_interpretation)
    elif analysis_type == AnalysisType.LIQUIDITY:
        return compute_liquidity_analysis(ticker, stock_data, with_interpretation)
    elif analysis_type == AnalysisType.PATTERN:
        return compute_pattern_analysis(ticker, stock_data, with_interpretation)
    else:
        return None
