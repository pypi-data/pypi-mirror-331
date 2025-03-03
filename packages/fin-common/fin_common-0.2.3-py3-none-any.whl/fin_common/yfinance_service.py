import yfinance as yf
import logging
import pandas as pd
from datetime import datetime
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter

# Enable DEBUG logging for requests_cache
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger("requests_cache")
# logger.setLevel(logging.DEBUG)

logging.getLogger("yfinance").setLevel(logging.ERROR)  # Suppress yfinance debug logs

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

session = CachedLimiterSession(
    limiter=Limiter(RequestRate(200, Duration.HOUR)),  # max 100 requests per hour
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)

def yf_download_data(ticker, period, interval):
    # print("Cached URLs:", list(session.cache.responses.keys()))
    try:
        return yf.download(ticker, period=period, interval=interval, session=session)
    except Exception as e:
        logging.error(f"Error occurred fetching stock data for {ticker}: {str(e)}")
        return None

def yf_get_info(ticker):
    # print("Cached URLs:", list(session.cache.responses.keys()))
    try:
        return yf.Ticker(ticker, session).info
    except Exception as e:
        logging.error(f"Error occurred fetching stock info for {ticker}: {str(e)}")
        return None

def yf_get_news(ticker):
    # print("Cached URLs:", list(session.cache.responses.keys()))
    try:
        return yf.Ticker(ticker, session=session).news
    except Exception as e:
        logging.error(f"Error occurred fetching stock news for {ticker}: {str(e)}")
        return []

# Langchain + Yfinance? https://python.langchain.com/docs/integrations/tools/yahoo_finance_news/
def get_yfinance_stock_news(ticker):
    news = yf_get_news(ticker)
    to_date = datetime.now().strftime('%Y-%m-%d')
    newest_news = [{
        'ticker': ticker,
        'headline': article['content']['title'],
        'url': article['content']['canonicalUrl']['url'],
        'summary': article['content']['summary'],
        'date': to_date
    } for article in news]
    return newest_news

def get_yfinance_indice_news():
    # could add more 
    major_indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']
    newest_news = []
    for ticker in major_indices:
        newest_news.extend(get_yfinance_stock_news(ticker))
    return newest_news

# First request should hit the API and store in cache, second request should hit the cache
# info1 = yf_get_info('AAPL')
# info2 = yf_get_info('AAPL')