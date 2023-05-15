from config import *
from utils import *

def get_eod_change_percents(startbuytime):
    orders = get_closed_orders(startbuytime)
    todays_buy_sell = {}
    for order in orders:
        if order.symbol not in todays_buy_sell:
            todays_buy_sell[order.symbol] = {'buy': 0, 'sell': 0, 'change': 0}
        if order.side == 'sell':
            todays_buy_sell[order.symbol]['sell'] += int(order.filled_qty) * float(order.filled_avg_price)
        elif order.side == 'buy':
            todays_buy_sell[order.symbol]['buy'] += int(order.filled_qty) * float(order.filled_avg_price)
    for ticker in todays_buy_sell:
        todays_buy_sell[ticker]['change'] = round((todays_buy_sell[ticker]['sell'] - todays_buy_sell[ticker]['buy']) / 
                                            todays_buy_sell[ticker]['buy'] * 100, 2)
        todays_buy_sell[ticker]['sell'] = round(todays_buy_sell[ticker]['sell'], 2)
        todays_buy_sell[ticker]['buy'] = round(todays_buy_sell[ticker]['buy'], 2)
    return todays_buy_sell

def save_data_to_csv(stock_data_csv, tradealgo):
    ...
