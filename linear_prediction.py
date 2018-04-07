import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import math
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression


class LinearPrediction(object):

    def relative_strength(self, prices, n=14):
        deltas = np.diff(prices)
        seed = deltas[:n+1]
        up = seed[seed >= 0].sum()/n
        down = -seed[seed < 0].sum()/n
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100./(1. + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(n - 1) + upval)/n
            down = (down*(n - 1) + downval)/n

            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)

        return rsi

    def forecast_out(self, dt, pair):
        df = pd.read_csv("ticker_data/"+pair+".csv", index_col=0)
        df = df[['OPEN', 'CLOSE', 'HIGH', 'LOW', ]]
        df['HL_PCT'] = ((df['LOW'] / df['HIGH']) -1) * 100 * -1
        df['PCT_Change'] = (df['CLOSE'] - df['OPEN']) / df['OPEN'] * 100
        df = df[['CLOSE', 'HIGH', 'LOW', 'HL_PCT', 'PCT_Change']]

        forecast_col = dt
        df.fillna(-99999, inplace=True)
        forecast_out = int(math.ceil(0.001*len(df)))
        df['label'] = df[forecast_col].shift(-forecast_out)

        X = np.array(df.drop(['label'],1))
        X = preprocessing.scale(X)
        X_lately = X[-forecast_out:]
        X = X[:-forecast_out:]

        df.dropna(inplace=True)
        y = np.array(df['label'])

        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.20)

        clf = LinearRegression()
        clf.fit(X_train, y_train)
        accuracy = clf.score(X_test, y_test)
        forecast_set = clf.predict(X_lately)
        # print(accuracy)
        return(forecast_set[-1])

    def percent_out(self, pair, p):
        df = pd.read_csv("ticker_data/"+pair+".csv", index_col=0)
        df = df[['HIGH', 'LOW', 'CLOSE']]
        HIGH = self.forecast_out('HIGH',pair)
        LOW = self.forecast_out('LOW',pair)
        CLOSE = self.forecast_out('CLOSE',pair)
        hl_pcnt = ((LOW / HIGH) -1) * 100 * -1
        data = {'predict_high': HIGH,
        'predict_low' : LOW,
        'predict_close' : CLOSE,
        'predict_hl_pcnt': hl_pcnt,
        'high' : df['HIGH'][df.index[-1]],
        'low' : df['LOW'][df.index[-1]],
        'close' : df['CLOSE'][df.index[-1]]}
        # return dict_data
        # print(data['close'])
        # print(data['predict_close'])
        # print(pair)
        # percent_change = (data['predict_close'] - data['close']) / data['close'] * 100
        # if percent_change > 3:
        hl_pcnt = ((data['predict_low'] / data['predict_high']) -1) * 100 * -1
        if hl_pcnt >= p:
                # print(self.format_float(data['predict_low']))
                # print(self.format_float(data['predict_high']))
                # print(pair)
            return data
        else:
            return None

    def format_float(self, f):
        # return format(f, '.8f')
        return '{:.8f}'.format(f)
