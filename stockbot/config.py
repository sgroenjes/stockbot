# stockbot config
import alpaca_trade_api as tradeapi
import pytz
from datetime import datetime, timedelta
import time
import requests

ALPACA_API_KEY = os.getenv('APCA_API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'
# APCA_API_BASE_URL = 'https://api.alpaca.markets'
TZ = pytz.timezone('America/New_York')

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

# url to nasdaq api
NASDAQ_API_URL = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=100&marketcap=large|mid|small&recommendation=strong_buy|buy"

STOCK_MAX_PRICE = 100
STOCK_MIN_PRICE = 20
MAX_NUM_STOCKS = 20
NUM_SHARES = 5
SELL_PERCENT_GAIN = 3
START_EQUITY = 5000
MOVED_DAYS = 5
MOVED_DAYS_CALC = 0

BUY_DAYS = [0,1,2,3,4]

# buy at open
BAO_GET_STOCKS_TIME = "8:30"
BAO_BUY_START_TIME = "9:30"
BAO_BUY_END_TIME = "11:00"
BAO_SELL_START_TIME = "11:00"
BAO_SELL_END_TIME = "15:30"

# buy at close
BAC_GET_STOCKS_TIME = "14:30"
BAC_BUY_START_TIME = "15:00"
BAC_BUY_END_TIME = "16:00"
BAC_SELL_START_TIME = "9:30"
BAC_SELL_END_TIME = "14:00"

