#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 05:24:15 2020

@author: yi
"""

import pandas as pd
import numpy as np
import pandas_datareader.data as web
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


def get_filing_return(ticker, filingdate):
    startdate = pd.to_datetime(filingdate)
    closeprice = web.DataReader(name=ticker.upper(), data_source='yahoo', start=filingdate, \
                                end=startdate + timedelta(10))[['Adj Close']]
    returns = closeprice.iloc[4] / closeprice.iloc[0] - 1
    return returns


def merge_return(data):
    data['excessret'] = np.nan
    for i in range(len(data)):
        tick = ticker[ticker[1] == data.iloc[i]['cik']].index[0]
        try:
            stockret = get_filing_return(tick, data.iloc[i]['filingdate'])
            benchmark = get_filing_return('^DJI', data.iloc[i]['filingdate'])
            excessret = stockret - benchmark
      
            data['excessret'][data.index == i] = excessret.values[0]
        except:
            pass
    return data
  

def quantile_calc(x, _quantiles = 5):
    return pd.qcut(x, _quantiles, labels=False) + 1


def get_result(ret_data):
    grouped_data = ret_data.copy()
    grouped_data = grouped_data.dropna()
    grouped_data['group'] = quantile_calc(grouped_data['% negative,'])
    result = grouped_data[['group', 'excessret']].groupby('group').agg({'excessret': 'median'})
    result.index = ['Low', '2', '3', '4', 'High']
    result['excessret'] = result['excessret'] * 100
    return result


if __name__ == '__main__':
    print('Getting Parser Data:')
    ticker = pd.read_csv('./ticker.txt', delimiter='\t', header=None, index_col=0)
    master_data = pd.read_csv('Parser_Clean.csv')
    harvard_data = pd.read_csv('Parser_Harvard_Clean.csv')

    print("Getting Return Data:")
    master_ret_data = merge_return(master_data)
    harvard_ret_data = merge_return(harvard_data)

    print('Getting Result:')
    master_result = get_result(master_ret_data)
    harvard_result = get_result(harvard_ret_data)

    _ = plt.plot(master_result, 'go-', label='Fin_Neg')
    _ = plt.plot(harvard_result, 'go-', label='Harvard_Neg')
    _ = plt.xlabel('Quintile(based on proportion of negative words)')
    _ = plt.ylabel('Median Filing Period Excess Return(%)')
    _ = plt.legend(loc='best')