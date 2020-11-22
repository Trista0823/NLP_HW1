#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 20:46:09 2020

@author: sunyingchao
"""


import pandas as pd
import numpy as np
import pandas_datareader.data as web
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

parser_data = pd.read_csv('Parser.csv')
parser_clean = pd.read_csv('Parser_Clean.csv', index_col = 0)
ticker = pd.read_csv('./ticker.txt', delimiter='\t', header=None, index_col = 0)
parser_data['filingdate'] = parser_data['file name,'].apply(lambda x: x[8:12] + '-' + x[12:14] + '-' + x[14:16])
parser_clean = parser_clean.drop(columns = ['co_tic'])
parser_clean = parser_clean.drop_duplicates()
data = parser_clean.merge(parser_data[['file size,', 'filingdate']])[['% negative,', 'cik', 'filingdate']]

def get_filing_return(ticker, filingdate):
    startdate = pd.to_datetime(filingdate)
    closeprice = web.DataReader(name = ticker.upper(), data_source = 'yahoo', start = filingdate, end = startdate + timedelta(10))[['Adj Close']]
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
  
      
ret_data = merge_return(data)

def quantile_calc(x, _quantiles = 5):
    return pd.qcut(x, _quantiles, labels=False) + 1

grouped_data = ret_data.copy()
grouped_data = grouped_data.dropna()
grouped_data['group'] = quantile_calc(grouped_data['% negative,'])
result = grouped_data[['group', 'excessret']].groupby('group').agg({'excessret': 'median'})
result.index = ['Low', '2', '3', '4', 'High']
result['excessret'] = result['excessret'] * 100

############################################
#### 这里还应该加上H4N-Inf的对比，但我没找到那个字典在哪
#####################################
_ = plt.plot(result, 'go-', label = 'Fin_Neg')
_ = plt.xlabel('Quintile(based on proportion of negative words)')
_ = plt.ylabel('Median Filing Period Excess Return(%)')
_ = plt.legend(loc = 'best')