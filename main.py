import logging
import time
import datetime
from dateutil import parser
from threading import Thread
from percent_change_data import PercentChangeData
from buy_sell import BuySell
from pairs import AllPairs

buy_sell = BuySell()
p = PercentChangeData()
pairs = AllPairs()

class percentChangeLine(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            print('\n Getting Percent Change \n')
            p.percent_change()
            time.sleep(3600)

class LinearPredictionLine(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            now = parser.parse(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            x = int(now.strftime("%M"))
            if x >= 0 and x <= 59:
                print('\n Deleting All Files From Linear Prediction Model \n')
                pairs.delete_all_data_files('ticker_data')
                time.sleep(5)
                print('\n Getting Ticker Data For Linear Prediction Model \n')
                p.get_ticker_data()
                
                print('\n Predicing A Buy From Linear Prediction Model \n')
                buy_sell.rsi_buy()
                time.sleep(1800)

class BuyAlgorithm(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            # time.sleep(300)
            buy_sell.buy_on_rise()
            # buy_sell.predictive_buy()
            time.sleep(600)

class SellAlgorithm(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:

            # buy_sell.sell_on_fall()
            buy_sell.arbitrage_sell()
            time.sleep(600)

class CancelUnsucessfulBuyOrders(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            buy_sell.cancel_old_orders()

class DeleteAllData(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            print('\n Deleting All Data \n')
            pairs.delete_all_data_files('data')
            time.sleep(86400)

class SellOldCoinsAtLoss(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            buy_sell.old_coins()
            time.sleep(1200)

def main():
    LinearPredictionLine()
    # percentChangeLine() # gets percent change every 60 seconds
    # BuyAlgorithm() # reads data to determine to buy based on percent change
    # SellAlgorithm() # Arbitrage sells coins
    # CancelUnsucessfulBuyOrders() # cancels all pending orders over 1 Hour old
    # DeleteAllData() # deletes all data on Start.
    # SellOldCoinsAtLoss() # Sells old coins at a loss after holding for 3 hours

if __name__ == "__main__":
    main()

    while True:
        pass
