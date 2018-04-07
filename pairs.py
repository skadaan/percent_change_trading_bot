import os
import glob
import csv
import pandas as pd
from pathlib import Path


class AllPairs(object):

    def get_current_pairs(self, folder):
        all_pairs = []
        list = glob.glob(folder+"/*.csv")
        for pair in list:
            c = pair.replace('.csv', '')
            f = c.replace(folder+'/', '')
            all_pairs.append(f)
        return all_pairs


    def delete_all_data_files(self, foldername):
        files = glob.glob(foldername+"/*.csv")
        for f in files:
            os.remove(f)

    def delete_file(self,filename):
        files = glob.glob("data/"+filename+".csv")
        for f in files:
            os.remove(f)

    # returns the last N=num data from the list.
    def crypto_pc_data(self, ticker, num, row_num):
        with open('ticker_data/'+ ticker +'.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            next(csvfile)
            data = []
            for row in readCSV:
                data.append(row[row_num])
        data = [ x for x in data ]
        return data[-num:]


    def pair_exists(self, pair):
        pair_file = Path('data/'+ pair +'.csv')
        if pair_file.is_file():
            return True

    # def get_list_len(self, pair, num, row_num):
    #     if len(self.crypto_pc_data(pair,num,row_num)) == num:
    #         return True
    #     else:
    #         return False
