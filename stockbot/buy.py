from config import *
from utils import *

def find_stocks(equity):
    stock_info = []
    data = get_nasdaq_buystocks()
    strong_buy_stocks = []

    for d in data['data']['table']['rows']:
        # Get daily price data for stock symbol over the last n trading days.
        barset = api.get_barset(d['symbol'], 'day', limit=MOVED_DAYS)
        if not barset[d['symbol']]:
            print('stock symbol {} not found'.format(d['symbol']))
            continue
        stock_bars = barset[d['symbol']]

        # See how much stock ticker moved in that timeframe.
        if MOVED_DAYS_CALC == 0:
            price_open = stock_bars[0].o
            price_close = stock_bars[-1].c
            percent_change = round((price_close - price_open) / price_open * 100, 3)
        else:
            prices = []
            x = 0
            while x < MOVED_DAYS:
                price_open = stock_bars[x].o
                price_close = stock_bars[x].c
                percent_change = round((price_close - price_open) / price_open * 100, 3)
                prices.append(percent_change)
                x += 1
            avg = round(sum(prices) / MOVED_DAYS, 3)
            percent_change = avg
            
        print('{} moved {}% over the last {} days'.format(d['symbol'], percent_change, MOVED_DAYS))
        
        strong_buy_stocks.append({'symbol': d['symbol'], 'company': d['name'], 
                                    'moved': percent_change})

    for stock_item in strong_buy_stocks:
        stock = stock_item['symbol']
        #print('DEBUG', stock)
        sys.stdout.write('.')
        sys.stdout.flush()

        data = get_stock_info(stock)
        if not data:
            print('stock symbol {} not found in yahoo finance'.format(stock))
            continue
        # check which market it's in
        exchange_name = data['chart']['result'][0]['meta']['exchangeName']
        if exchange_name not in ['NYQ', 'NMS']:
            print('stock symbol {} in different exchange {}'.format(stock, exchange_name))
            continue

        try:
            stock_high = round(data['chart']['result'][0]['indicators']['quote'][0]['high'][1], 2)
        except Exception:
            stock_high = round(data['chart']['result'][0]['indicators']['quote'][0]['high'][0], 2)

        try:
            stock_low = round(data['chart']['result'][0]['indicators']['quote'][0]['low'][1], 2)
        except Exception:
            stock_low = round(data['chart']['result'][0]['indicators']['quote'][0]['low'][0], 2)

        change_low_to_high = round(stock_high - stock_low, 3)

        stock_price = get_stock_price(data)

        try:
            stock_volume = data['chart']['result'][0]['indicators']['quote'][0]['volume'][1]
        except Exception:
            stock_volume = data['chart']['result'][0]['indicators']['quote'][0]['volume'][0]

        if stock_price > STOCK_MAX_PRICE or stock_price < STOCK_MIN_PRICE:
            continue

        change_low_to_market = round(stock_price - stock_low, 3)

        stock_info.append({'symbol': stock, 'company': stock_item['company'], 
                            'market_price': stock_price, 'low': stock_low, 
                            'high': stock_high, 'volume': stock_volume,
                            'change_low_to_high': change_low_to_high,
                            'change_low_to_market': change_low_to_market,
                            'moved': stock_item['moved']})

    # sort stocks
    if tradealgo == 'moved':
        biggest_movers = sorted(stock_info, key = lambda i: i['moved'], reverse = True)
    elif tradealgo == 'lowtomarket':
        biggest_movers = sorted(stock_info, key = lambda i: i['change_low_to_market'], reverse = True)
    elif tradealgo == 'lowtohigh':
        biggest_movers = sorted(stock_info, key = lambda i: i['change_low_to_high'], reverse = True)

    stock_picks = biggest_movers[0:MAX_NUM_STOCKS]
    print('\n')

    print(datetime.now(tz=TZ).isoformat())
    print('today\'s stocks {}'.format(stock_info))
    print('\n')
    print('today\'s picks {}'.format(stock_picks))
    print('\n')
    return biggest_movers, stock_picks

def buy_stocks():
    stock_prices = []
    stock_bought_prices = []
    bought_stocks = []

    total_buy_price = 0
    while True:
        for stock in stock_picks:
            already_bought = False
            for stockval in stock_bought_prices:
                if stockval[0] == stock['symbol']:
                    already_bought = True
                    break
            if already_bought:
                continue

            data = get_stock_info(stock['symbol'])
            stock_price_buy = get_stock_price(data)

            # count the number of stock prices for the stock we have
            num_prices = 0
            went_up = 0
            went_down = 0
            for stockitem in stock_prices:
                if stockitem[0] == stock['symbol']:
                    num_prices +=1
                    # check prev. price compared to now to see if it went up or down
                    if stock_price_buy > stockitem[1]:
                        went_up += 1
                    else:
                        went_down += 1

            # buy the stock if there are 5 records of it and it's gone up and if we have
            # enough equity left to buy
            # if buying at end of day, ignore record checking to force it to buy

            if startbuytime == 'buyatclose':
                n = 0
                went_up = 1
                went_down = 0
            else:
                n = 5
            buy_price = stock_price_buy * NUM_SHARES
            if num_prices >= n and went_up > went_down and equity >= buy_price:
                buy_time = datetime.now(tz=TZ).isoformat()
                print(buy_time)
                alpaca_order(stock['symbol'], side='buy')
                print('placed buy order of stock {} ({}) for ${} (vol {})'.format(
                    stock['symbol'], stock['company'], stock_price_buy, stock['volume']))
                total_buy_price += buy_price
                stock_bought_prices.append([stock['symbol'], stock_price_buy, buy_time])
                bought_stocks.append(stock)
                equity -= buy_price
            
            stock_prices.append([stock['symbol'], stock_price_buy])

        # sleep and check prices again after 2 min if time is before 11:00am EST / 4:00pm EST (market close)
        if len(stock_bought_prices) == MAX_NUM_STOCKS or \
            equity == 0 or \
            (datetime.now(tz=TZ).hour == buy_eh and datetime.now(tz=TZ).minute >= buy_em):
            break
        else:
            time.sleep(120)
    
    print(datetime.now(tz=TZ).isoformat())
    print('sent buy orders for {} stocks, market price ${}'.format(len(bought_stocks), round(total_buy_price, 2)))
    if startbuytime == 'buyatclose':
        print('holding these stocks and selling them the next market open day...')
    print('\n')
    return bought_stocks, stock_bought_prices