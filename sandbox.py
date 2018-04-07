from bittrex import Bittrex
from pairs import AllPairs
from buy_sell import BuySell
from percent_change_data import PercentChangeData
import time
import datetime
from dateutil import parser
import numpy as np
import pandas as pd
import os.path
import csv
import matplotlib.pyplot as plt
from linear_prediction import LinearPrediction

import matplotlib.finance as finance

all_pairs = AllPairs()
buy_sell = BuySell()
percent_change = PercentChangeData()
linear_prediction = LinearPrediction()
V2_bittrex = Bittrex('pub', 'pri',api_version='v2.0')


my_bittrex = Bittrex('pub', 'pri')

def last_price(ticker):
    coin_current_price = my_bittrex.get_marketsummary('BTC-'+ticker)['result']
    return coin_current_price[0]['Last']

def my_percent_change_coins():
    try:
        x_list = ['SAFEX', 'SNGLS', 'CLUB']
        my_coins = []
        holding_coins = my_bittrex.get_balances()['result']
        print('\n')
        print('Currency\t Bought at\t Last Closed\t Percent Change\t Timestamp')
        print('____________________________________________________________________________')
        for coins in holding_coins:
            if coins['Balance'] >= 1 and coins['Currency'] not in x_list:
                my_coins.append(coins['Currency'])

        # print(my_coins)
        for holding in my_coins:
            order_history = my_bittrex.get_order_history('BTC-' + holding)['result']
            if len(order_history) > 0:
                order_date = parser.parse(order_history[0]['TimeStamp']).strftime("%m/%d/%Y %H:%M:%S")
                percent_change = ((last_price(holding) - order_history[0]['PricePerUnit'])/order_history[0]['PricePerUnit'] * 100)
                print(holding + '\t\t' + str(buy_sell.format_float(order_history[0]['PricePerUnit'])) + '\t' + str(buy_sell.format_float(last_price(holding)))
                + '\t' + str(int(percent_change)) + '%'+ '\t\t' + order_date)
    except Exception as e:
        # print(e)
        pass

# Gets current percent change of sold orders
def previous_sold_orders():
    my_orders = my_bittrex.get_order_history()['result']
    for order in my_orders:
        if '2018-01-07' in order['TimeStamp']:
            paid = order['PricePerUnit']
            last_closed = last_price(order['Exchange'].replace('BTC-', ''))
            percent_change = ((last_closed - paid)/paid * 100)
            print(percent_change)

def get_ticker_data():
    info_file = "data/1stest.csv"
    file_exists = os.path.isfile(info_file)
    with open(info_file, "a") as data_file:
        headers = [ 'TIMESTAMP', 'BITCOIN_VOLUME', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']
        writer = csv.DictWriter(data_file, delimiter=',', lineterminator='\n',fieldnames=headers)
        if not file_exists:
            data = V2_bittrex.get_candles('BTC-ETC', 'thirtyMin')['result']
            writer.writeheader()  # file doesn't exist yet, write a header
        else:
            data = V2_bittrex.get_latest_candle('BTC-ETC', 'thirtyMin')['result']
            print('else')
        for tick in data:
            writer.writerow({'TIMESTAMP' : tick['T'],
            'BITCOIN_VOLUME': tick['BV'],
            'OPEN' : tick['O'],
            'CLOSE': tick['C'],
            'HIGH': tick['H'],
            'LOW' : tick['L'],
            'VOLUME' : tick['V']})

# =SUM((F2/E2)-1)*100*-1

def cancel_old_orders(self):
    try:
        if len(my_bittrex.get_open_orders()['result']) > 0:
            for buy_order in my_bittrex.get_open_orders()['result']:
                if buy_order['OrderType'] == 'LIMIT_BUY':
                    time_opened = parser.parse(str(buy_order['Opened'])).strftime("%Y-%m-%d %H:%M:%S")
                    now = parser.parse(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
                    difference = now - parser.parse(time_opened)
                    if int(parser.parse(str(difference)).strftime("%M")) >= 30:
                        my_bittrex.cancel(buy_order['OrderUuid'])
                        print('Canceled Limit Buy order for ' + buy_order['Exchange'])
    except Exception as e:
        print('error with coing: ' +buy_order['Exchange'] + '\n')
        print(e)
#
#
#
# def relative_strength(prices, n=14):
#     deltas = np.diff(prices)
#     seed = deltas[:n+1]
#     up = seed[seed >= 0].sum()/n
#     down = -seed[seed < 0].sum()/n
#     rs = up/down
#     rsi = np.zeros_like(prices)
#     rsi[:n] = 100. - 100./(1. + rs)
#
#     for i in range(n, len(prices)):
#         delta = deltas[i - 1]  # cause the diff is 1 shorter
#
#         if delta > 0:
#             upval = delta
#             downval = 0.
#         else:
#             upval = 0.
#             downval = -delta
#
#         up = (up*(n - 1) + upval)/n
#         down = (down*(n - 1) + downval)/n
#
#         rs = up/down
#         rsi[i] = 100. - 100./(1. + rs)
#
#     return rsi
#
# pairs = all_pairs.get_current_pairs('ticker_data')
# for pair in pairs:
#     try:
#         if linear_prediction.percent_out(pair, 3) is not None:
#             print(pair)
#             print(linear_prediction.percent_out(pair,3), '\n')
#     except Exception as e:
#         # print('error with coing: ' +buy_order['Exchange'] + '\n')
#         print(e)

my_percent_change_coins()
