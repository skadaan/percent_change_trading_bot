from bittrex import Bittrex
import requests
import csv
from pairs import AllPairs
import pandas as pd
import numpy as np
import os.path
import datetime
from dateutil import parser
import time

my_bittrex = Bittrex('pub', 'pri')
V2_bittrex = Bittrex('pub', 'pri',api_version='v2.0')
all_pairs = AllPairs()



class PercentChangeData(object):
    def collect_data(self, ticker, change, prevDay, lastPrice, volume, ask, bid, ticker_change):
        info_file = "data/"+ticker+'.csv'
        file_exists = os.path.isfile(info_file)
        with open(info_file, "a") as data_file:
            headers = ['TIMESTAMP', 'VOLUME', 'CHANGE', 'PREV_DAY', 'LAST', 'ASK', 'BID', 'TICKER_CHANGE']
            writer = csv.DictWriter(data_file, delimiter=',', lineterminator='\n',fieldnames=headers)
            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header

            timestamp = parser.parse(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
            writer.writerow({'TIMESTAMP' : timestamp,
            'CHANGE': change,
            'VOLUME' : volume,
            'PREV_DAY': self.format_float(prevDay),
            'LAST': self.format_float(lastPrice),
            'ASK' : self.format_float(ask),
            'BID' : self.format_float(bid),
            'TICKER_CHANGE' : self.format_float(ticker_change)})

    def percent_change(self):
        try:
            for crypto in my_bittrex.get_market_summaries()['result']:
                data = (crypto['MarketName'],
                crypto['PrevDay'],
                crypto['Last'],
                crypto['Volume'],
                crypto['Bid'],
                crypto['Ask'])
                # volume_24h = self.get_24h_volume(data[0].replace('BTC-', ''))
                # last = str(self.format_float(data[2])).replace('.', '')
                if 'BTC-' in crypto['MarketName']:
                    if (data[3] is not None and data[3] > 499999):
                        percentage_change = ((data[2] - data[1])/data[1] * 100)
                        if data[0] not in all_pairs.get_current_pairs('data'):
                            ticker = V2_bittrex.get_latest_candle(data[0], 'thirtyMin')['result'][0]['L']
                            ticker_percent_change = ((data[2] - ticker)/ticker * 100)
                            if percentage_change >= -5 and percentage_change < 25 and crypto['Bid'] > 0.00000000 and crypto['Ask'] > 0.00000000:
                                self.collect_data(ticker=data[0],
                                change=percentage_change,
                                prevDay=data[1],
                                volume=data[3],
                                lastPrice=data[2],
                                bid=data[4],
                                ask=data[5],
                                ticker_change=ticker_percent_change)
                        else:
                            ticker = float(all_pairs.crypto_pc_data(data[0], 1, 4)[0])
                            ticker_percent_change = ((data[2] - ticker)/ticker * 100)
                            self.collect_data(ticker=data[0],
                            change=percentage_change,
                            prevDay=data[1],
                            volume=data[3],
                            lastPrice=data[2],
                            bid=data[4],
                            ask=data[5],
                            ticker_change=ticker_percent_change)
        except Exception as e:
            print(data[0])
            print(e)

    def get_ticker_data(self):
        try:
            ticker_time = 'thirtyMin'
            for crypto in my_bittrex.get_market_summaries()['result']:
                if 'BTC-' in crypto['MarketName'] and crypto['Volume'] >= 500000:
                    info_file = "ticker_data/"+crypto['MarketName']+".csv"
                    file_exists = os.path.isfile(info_file)
                    with open(info_file, "a") as data_file:
                        headers = [ 'TIMESTAMP', 'BITCOIN_VOLUME', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']
                        writer = csv.DictWriter(data_file, delimiter=',', lineterminator='\n',fieldnames=headers)
                        if not file_exists:
                            data = V2_bittrex.get_candles(crypto['MarketName'], ticker_time)['result']
                            writer.writeheader()  # file doesn't exist yet, write a header
                        else:
                            data = V2_bittrex.get_latest_candle(crypto['MarketName'], ticker_time)['result']
                            print('else')
                        for tick in data:
                            writer.writerow({'TIMESTAMP' : tick['T'],
                            'BITCOIN_VOLUME': tick['BV'],
                            'OPEN' : self.format_float(tick['O']),
                            'CLOSE': self.format_float(tick['C']),
                            'HIGH': self.format_float(tick['H']),
                            'LOW' : self.format_float(tick['L']),
                            'VOLUME' : tick['V']})
        except Exception as e:
            print(crypto['MarketName'])
            print(e)

    def uptrend(self, list):
        x = 0
        indicator = 0
        while x < len(list) - 1:
            if list[x] < list[x + 1]:
                indicator += 1
            x += 1
        # percent = ((list[len(list) - 1] - list[0]) / list[0] * 100)
        by_one = float(list[len(list) -1]) - float(list[0])
        if int(len(list) * .75) <= indicator and list[0] < list[len(list) -1] and by_one >= 1:
            return True
        else:
            return False

    def downtrend(self, list):
        x = 0
        indicator = 0
        while x < len(list) - 1:
            if list[x] > list[x + 1]:
                indicator += 1
            x += 1
        if int(len(list) * .75) <= indicator and list[0] > list[len(list) -1]:
            return True
        else:
            return False

    def format_float(self, f):
        # return format(f, '.8f')
        return '{:.8f}'.format(f)


    def simple_request(self, url):
        r = requests.get(url)
        return r.json()
