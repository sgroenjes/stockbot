from config import *
from utils import *

def sell_stocks(stock_bought_prices, bought_stocks):
    stock_prices = []
    stock_sold_prices = []
    stock_data_csv = [['symbol', 'company', 'buy', 'buy time', 'sell', 'sell time', 'profit', 'percent', 'vol sod', 'vol sell']]

    while True:
        for stock in bought_stocks:
            already_sold = False
            for stockval in stock_sold_prices:
                if stockval[0] == stock['symbol']:
                    already_sold = True
                    break
            if already_sold:
                continue

            data = get_stock_info(stock['symbol'])
            stock_price_sell = get_stock_price(data)

            stockinfo = [ x for x in stock_bought_prices if x[0] is stock['symbol'] ]
            stock_price_buy = stockinfo[0][1]
            buy_time = stockinfo[0][2]

            # sell the stock if it's gone up by x percent
            change_perc = round((stock_price_sell - stock_price_buy) / stock_price_buy * 100, 2)
            sell_time = datetime.now(tz=TZ).isoformat()
            diff = round(stock_price_sell - stock_price_buy, 2)
            if change_perc >= SELL_PERCENT_GAIN:
                print(sell_time)
                alpaca_order(stock['symbol'], side='sell')
                stock_data = get_stock_info(stock['symbol'])
                stock_vol_now = stock_data['chart']['result'][0]['indicators']['quote'][0]['volume'][0]
                print('placed sell order of stock {} ({}) for ${} (diff ${} {}%) (vol {})'.format(
                    stock['symbol'], stock['company'], stock_price_sell, diff, change_perc, stock_vol_now))
                sell_price = stock_price_sell * NUM_SHARES
                stock_data = get_stock_info(stock['symbol'])
                stock_vol_now = stock_data['chart']['result'][0]['indicators']['quote'][0]['volume'][0]
                stock_data_csv.append([stock['symbol'], stock['company'], stock_price_buy, buy_time, 
                                        stock_price_sell, sell_time, diff, change_perc, stock['volume'], stock_vol_now])
                stock_sold_prices.append([stock['symbol'], stock_price_sell, sell_time])
                equity += sell_price
            else:
                print(sell_time)
                print('stock {} ({}) hasn\'t gone up enough to sell ${} (diff ${} {}%)'.format(
                    stock['symbol'], stock['company'], stock_price_sell, diff, change_perc))

        # sleep and check prices again after 2 min if time is before 1:00pm EST
        if len(stock_sold_prices) == len(bought_stocks) or \
            (datetime.now(tz=TZ).hour == 13 and datetime.now(tz=TZ).minute >= 0):  # 1:00pm EST
            break
        else:
            time.sleep(120)

    if len(stock_sold_prices) < len(bought_stocks) and \
        (datetime.now(tz=TZ).hour == 13 and datetime.now(tz=TZ).minute >= 0):  # 1:00pm EST
    
        print(datetime.now(tz=TZ).isoformat())
        print('selling any remaining stocks if they go down, or else sell at end of day...')

        while True:
            for stock in bought_stocks:
                already_sold = False
                for stockval in stock_sold_prices:
                    if stockval[0] == stock['symbol']:
                        already_sold = True
                        break
                if already_sold:
                    continue

                data = get_stock_info(stock['symbol'])
                stock_price_sell = get_stock_price(data)

                # count the number of stock prices for the stock we have
                num_prices = 0
                went_up = 0
                went_down = 0
                for stockitem in stock_prices:
                    if stockitem[0] == stock['symbol']:
                        num_prices +=1
                        # check prev. price compared to now to see if it went up or down
                        if stock_price_sell > stockitem[1]:
                            went_up += 1
                        else:
                            went_down += 1

                stock_prices.append([stock['symbol'], stock_price_sell])

                # sell the stock if there are 15 records of it and it's gone down
                # or sell if it's the end of the day
                if (num_prices >= 15 and went_down > went_up) or (datetime.now(tz=TZ).hour == sell_eh \
                    and datetime.now(tz=TZ).minute >= sell_em):
                    stockinfo = [ x for x in stock_bought_prices if x[0] is stock['symbol'] ]
                    stock_price_buy = stockinfo[0][1]
                    buy_time = stockinfo[0][2]
                    diff = round(stock_price_sell - stock_price_buy, 2)
                    change_perc = round((stock_price_sell - stock_price_buy) / stock_price_buy * 100, 2)
                    sell_time = datetime.now(tz=TZ).isoformat()
                    print(sell_time)
                    alpaca_order(stock['symbol'], side='sell')
                    stock_data = get_stock_info(stock['symbol'])
                    stock_vol_now = stock_data['chart']['result'][0]['indicators']['quote'][0]['volume'][0]
                    print('placed sell order of stock {} ({}) for ${} (diff ${} {}%) (vol {})'.format(
                        stock['symbol'], stock['company'], stock_price_sell, diff, change_perc, stock_vol_now))
                    sell_price = stock_price_sell * NUM_SHARES
                    stock_data_csv.append([stock['symbol'], stock['company'], stock_price_buy, buy_time, 
                                            stock_price_sell, sell_time, diff, change_perc, stock['volume'], stock_vol_now])
                    stock_sold_prices.append([stock['symbol'], stock_price_sell, sell_time])
                    equity += sell_price

            # sleep and check prices again after 2 min if time is before # 3:30pm EST / 2:30pm EST (buy at close)
            if len(stock_sold_prices) == len(bought_stocks) or \
                (datetime.now(tz=TZ).hour == sell_eh and datetime.now(tz=TZ).minute >= sell_em):
                break
            time.sleep(120)

        # sold all stocks or market close

        percent = round((equity - START_EQUITY) / START_EQUITY * 100, 2)
        equity = round(equity, 2)
        print(datetime.now(tz=TZ).isoformat())
        print('*** PERCENT {}%'.format(percent))
        print('*** EQUITY ${}'.format(equity))

        # wait until end of day for all the final sells and
        # print an Alpaca stock summary
        print('waiting for Alpaca report...')
        while True:
            if datetime.now(tz=TZ).hour == sell_eh and datetime.now(tz=TZ).minute >= sell_em + 5:
                break
            time.sleep(60)

        # print out summary of today's buy/sells on alpaca

        todays_buy_sell = get_eod_change_percents(startbuytime)
        print(datetime.now(tz=TZ).isoformat())
        print(todays_buy_sell) 
        print('********************')
        print('TODAY\'S PROFIT/LOSS')
        print('********************')
        total_profit = 0
        total_buy = 0
        total_sell = 0
        n = 0
        stock_data_csv.append([])
        stock_data_csv.append(['symbol', 'buy', 'sell', 'change'])
        for k, v in todays_buy_sell.items():
            change_str = '{}{}'.format('+' if v['change']>0 else '', v['change'])
            print('{} {}%'.format(k, change_str))
            stock_data_csv.append([k, v['buy'], v['sell'], v['change']])
            total_profit += v['change']
            total_buy += v['buy']
            total_sell += v['sell']
            n += 1
        print('-------------------')
        sum_str = '{}{}%'.format('+' if v['change']>0 else '', round(total_profit, 2))
        avg_str = '{}{}%'.format('+' if v['change']>0 else '', round(total_profit/n, 2))
        buy_str = '${}'.format(round(total_buy, 2))
        sell_str = '${}'.format(round(total_sell, 2))
        profit_str = '${}'.format(round(total_sell - total_buy, 2))
        print('*** SUM {}'.format(sum_str))
        print('*** AVG {}'.format(avg_str))
        print('*** BUY {}'.format(buy_str))
        print('*** SELL {}'.format(sell_str))
        print('*** PROFIT/LOSS {}'.format(profit_str))

        # write csv

        now = datetime.now(tz=TZ).date().isoformat()
        csv_file = 'stocks_{0}_{1}.csv'.format(tradealgo, now)
        f = open(csv_file, 'w')

        with f:
            writer = csv.writer(f)
            for row in stock_data_csv:
                writer.writerow(row)
            writer.writerow([])
            writer.writerow(["PERCENT", percent])
            writer.writerow(["EQUITY", equity])
            writer.writerow([])
            writer.writerow(["SUM", sum_str])
            writer.writerow(["AVG", avg_str])
            writer.writerow([])
            writer.writerow(["BUY", buy_str])
            writer.writerow(["SELL", sell_str])
        
        # set equity back to start value to not reinvest any gains
        if equity > START_EQUITY:
            equity = START_EQUITY

    return stock_data_csv, equity
