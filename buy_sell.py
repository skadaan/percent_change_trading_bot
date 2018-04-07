import csv
from pairs import AllPairs
import pandas as pd
from bittrex import Bittrex
import datetime
from dateutil import parser
import time
from percent_change_data import PercentChangeData
from linear_prediction import LinearPrediction

my_bittrex = Bittrex('pub', 'pri')
all_pairs = AllPairs()
percent_change = PercentChangeData()
linear_prediction = LinearPrediction()


class BuySell(object):

    def buy_on_rise(self):
        buy_pairs = self.get_hodl_bags()
        open_buy_orders = self.open_buy_orders()
        for pair in all_pairs.get_current_pairs('data'):
            x = 2
            try:
                data = all_pairs.crypto_pc_data(pair, x, 2)
                if pair not in buy_pairs and pair not in open_buy_orders and pair in all_pairs.get_current_pairs('ticker_data'):
                    predict_data = linear_prediction.percent_out(pair, 4)
                    if len(data) == x and predict_data is not None:

                        predict_low = float(self.format_float(predict_data['predict_low']))
                        predict_close = float(self.format_float(predict_data['predict_close']))
                        last_close = float(self.format_float(predict_data['close']))
                        current_bid_price = float((self.format_float(self.get_price(pair, 'Bid'))))

                        if percent_change.uptrend(data) is True and predict_close > last_close:
                            if self.total_coins_in_bitcoin(pair) < .007:
                                last = self.get_price(pair, 'Bid')
                                bid_price = self.buy_price(pair, 'Bid', 1.025)
                                # print('buying '+pair +' price at: ' +str(self.format_float(bid_price)) + ' for a total of: ' + str(bid_price  * self.units_order(bid_price))  + ' units')
                                res = my_bittrex.buy_limit(pair, self.units_order(bid_price), bid_price)
                                print(res)
                                print('straight uptrend')
                                all_pairs.delete_file(pair)
                    #     else:
                    #         print('down trending '+pair)
                    # else:
                    #     print('still gathering data for: '+pair)
            except Exception as e:
                print('\nexception occured: ' + pair)
                print(e)
                print('\n')
                pass

    def predictive_buy(self):
        x_list = ['SAFEX', 'SNGLS', 'BTC', 'BTG', 'CLUB', 'ARDR']
        buy_pairs = self.get_hodl_bags()
        open_buy_orders = self.open_buy_orders()
        for pair in all_pairs.get_current_pairs('ticker_data'):
            if pair not in buy_pairs and pair not in open_buy_orders and pair not in x_list:
                if self.total_coins_in_bitcoin(pair) < .0007:
                    predict_data = linear_prediction.percent_out(pair, 3.5)
                    if predict_data is not None:
                        predict_low = float(self.format_float(predict_data['predict_low']))
                        predict_close = float(self.format_float(predict_data['predict_close']))
                        last_close = float(self.format_float(predict_data['close']))
                        current_bid_price = float((self.format_float(self.get_price(pair, 'Bid'))))
                        if predict_close > last_close:
                            if predict_low < current_bid_price:
                                print(self.format_float(predict_low))
                                res = my_bittrex.buy_limit(pair, self.units_order(predict_low), predict_low)
                                print(pair)
                                print(res)
                                print('\n')

    def sell_on_fall(self):
        try:
            for pair in self.get_hodl_bags():
                pending_order = my_bittrex.get_open_orders(pair)['result']
                x = 10
                if pair in all_pairs.get_current_pairs() and len(all_pairs.crypto_pc_data(pair, x)) == x:
                    data = all_pairs.crypto_pc_data(pair, x, 2)
                    if percent_change.downtrend(data) is True:
                        balance_result = my_bittrex.get_balance(pair)['result']
                        if balance_result is not None:
                            print('selling '+pair)
                            res = my_bittrex.sell_limit(pair, balance_result['Balance'], self.get_price(pair, 'Bid'))
                            print(res)
        except Exception as e:
            print(e)

    def arbitrage_sell(self):
        try:
            x_list = ['SAFEX', 'SNGLS', 'BTC', 'BTG', 'CLUB']
            my_coins = []
            holding_coins = my_bittrex.get_balances()['result']

            for coins in holding_coins:
                if coins['Available'] > 0 and coins['Currency'] not in x_list:
                    my_coins.append(coins['Currency'])

            for hodling in my_coins:
                # if self.total_coins_in_bitcoin('BTC-'+hodling) >= 0.001:
                order_history = my_bittrex.get_order_history('BTC-' + hodling)['result']
                total_coins = my_bittrex.get_balance(hodling)['result']['Available']
                res = my_bittrex.sell_limit('BTC-' + hodling, total_coins, order_history[0]['PricePerUnit'] * 1.01)
                print('selling '+hodling)
                print(res)
        except Exception as e:
            print(hodling)
            print(e)

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
            # print('error with coin: ' +buy_order['Exchange'] + '\n')
            print(e)

    def old_coins(self):
        try:
            open_orders = my_bittrex.get_open_orders()['result']
            if len(open_orders) > 0:
                for buy_order in open_orders:

                    pair = buy_order['Exchange']
                    balance = my_bittrex.get_balance(buy_order['Exchange'].replace('BTC-', ''))['result']['Balance']
                    bid = my_bittrex.get_marketsummary(buy_order['Exchange'])['result'][0]['Bid']

                    if buy_order['OrderType'] == 'LIMIT_SELL':
                        timestamp_bought = parser.parse(buy_order['Opened'])
                        time_bought = parser.parse(str(timestamp_bought)).strftime("%Y-%m-%d %H:%M:%S")
                        now = parser.parse(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))

                        difference = now - parser.parse(time_bought)
                        if balance > 0 and int(parser.parse(str(difference)).strftime("%H")) >= 20:
                            cancel_old_coins = my_bittrex.cancel(buy_order['OrderUuid'])
                            time.sleep(5)
                            sell_at_loss = my_bittrex.sell_limit(pair, balance, bid)
                            time.sleep(3)
        except Exception as e:
            print('error with coin: ' + buy_order['Exchange'] + '\n')
            print(e)

    def get_hodl_bags(self):
        try:
            my_coins = []
            for balance in my_bittrex.get_balances()['result']:
                if balance['Balance'] > 0:
                    my_coins.append('BTC-'+balance['Currency'])
            return my_coins
        except Exception as e:
            print(e)

    def open_buy_orders(self):
        pending_order = my_bittrex.get_open_orders()
        open_buy_orders = []
        for coins in pending_order['result']:
            if coins['OrderType'] == 'LIMIT_BUY':
                open_buy_orders.append(coins['Exchange'])

        return open_buy_orders

    def get_price(self, pair, type):
        crypto = my_bittrex.get_marketsummary(pair)['result'][0]
        return crypto[type]

    def buy_price(self, pair, type, low=None):
        price = self.get_price(pair, type)
        if low is not None:
            low_price = price * low
            bid_price = price - low_price
        return price

    def total_coins_in_bitcoin(self, ticker):
        coin_current_price = my_bittrex.get_marketsummary(ticker)['result']
        coin_balanace = 0
        for coins in my_bittrex.get_balances()['result']:
            if coins is not None:
                if coins['Currency'] == ticker:
                    coin_balanace = coins['Available']
        return (coin_balanace * coin_current_price[0]['Last'])

    def format_float(self, f):
        # return format(f, '.8f')
        return '{:.8f}'.format(f)

    def units_order(self, last):
        return 0.0011 / last
