# import os, sys
# import csv
# import requests
# import urllib.request
# import time
# import optparse
# from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
# from datetime import date, datetime, timedelta
# from pytz import timezone
# from random import randint
# from urllib.parse import urlparse

# from config import *

# import alpaca_trade_api as tradeapi
# from alpaca_trade_api.rest import APIError

from stockbot import buy, sell, report

STOCKBOT_VERSION = '0.1.0'
__version__ = STOCKBOT_VERSION

def main():
    usage = """Usage: stockbot.py [-h] [-t tradealgo] [-b startbuytime]

StockBot v{0}
Alpaca algo stock trading bot.""".format(STOCKBOT_VERSION)
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-t', '--tradealgo', default='moved', 
                        help='algo to use for trading, options are moved, lowtomarket or lowtohigh, default "%default"')
    parser.add_option('-b', '--startbuytime', default='buyatopen', 
                        help='when to starting buying stocks, options are buyatopen, and buyatclose, default "%default"')
    options, args = parser.parse_args()
    
    # print banner
    banner = """\033[32m                                
    _____ _           _   _____     _   
    |   __| |_ ___ ___| |_| __  |___| |_ 
    |__   |  _| . |  _| '_| __ -| . |  _|
    |_____|_| |___|___|_,_|_____|___|_|  
    StockBot v{0}    +$ = :)  -$ = ;(\n
    https://github.com/sgroenjes/stockbot\033[0m\n\n""".format(STOCKBOT_VERSION)

    print(banner)
    
    tradealgo = options.tradealgo
    startbuytime = options.startbuytime

    print('Trade algo: {}'.format(tradealgo))
    print('Buy time: {}'.format(startbuytime))

    # Get our account information.
    account = api.get_account()
    
    print('Account info:')
    print(account)

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')
        sys.exit(0)
        
    # List current positions
    print('Current positions:')
    print(api.list_positions())

    equity = START_EQUITY

    # times to buy/sell

    if startbuytime == 'buyatopen':
        get_stocks_h, get_stocks_m = BAO_GET_STOCKS_TIME.split(':')
        buy_sh, buy_sm = BAO_BUY_START_TIME.split(':')
        buy_eh, buy_em = BAO_BUY_END_TIME.split(':')
        sell_sh, sell_sm = BAO_SELL_START_TIME.split(':')
        sell_eh, sell_em = BAO_SELL_END_TIME.split(':')
    else:  # buy at close
        get_stocks_h, get_stocks_m = BAC_GET_STOCKS_TIME.split(':')
        buy_sh, buy_sm = BAC_BUY_START_TIME.split(':')
        buy_eh, buy_em = BAC_BUY_END_TIME.split(':')
        sell_sh, sell_sm = BAC_SELL_START_TIME.split(':')
        sell_eh, sell_em = BAC_SELL_END_TIME.split(':')

    while True:
        try:
            if datetime.today().weekday() in BUY_DAYS and datetime.now(tz=TZ).hour == get_stocks_h \
                and datetime.now(tz=TZ).minute == get_stocks_m:
                print(datetime.now(tz=TZ).isoformat())
                print('getting buy and strong buy stocks from Nasdaq.com...')
                # find_stocks

            # buy stocks
            if datetime.today().weekday() in [0,1,2,3,4] and datetime.now(tz=TZ).hour == buy_sh \
                and datetime.now(tz=TZ).minute == buy_sm:
                print(datetime.now(tz=TZ).isoformat())
                print('starting to buy stocks...')
                # buy_stocks

            # sell stocks
            if datetime.today().weekday() in [0,1,2,3,4] and datetime.now(tz=TZ).hour == sell_sh \
                and datetime.now(tz=TZ).minute >= sell_sm:
                print(datetime.now(tz=TZ).isoformat())
                print('selling stock if it goes up by {}%...'.format(SELL_PERCENT_GAIN))
                # sell_stocks
                
            print(datetime.now(tz=TZ).isoformat(), '$ zzz...')
            time.sleep(60)

        except KeyboardInterrupt:
            print('Ctrl+c pressed, exiting')

if __name__ == "__main__":
    main()
