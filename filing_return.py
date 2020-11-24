#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 05:24:15 2020

@author: yi
"""

import re
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


def clean_parser(file):

    def cik_cut(s):
        pattern = ("(?<=_).*?(?=_)")
        result = re.findall(pattern, s)
        return result[0]

    parser = pd.read_csv(file)
    ticker = pd.read_csv('ticker.txt', delimiter='\t', header=None)
    ticker = ticker.rename(columns={0: 'co_tic', 1: 'cik'})

    parser['filingdate'] = parser['file name,'].apply(lambda x: x[8:12] + '-' + x[12:14] + '-' + x[14:16])
    parser['file name,'] = parser['file name,'].apply(lambda x: x[32:42])
    parser['cik'] = parser['file name,'].apply(lambda x: int(cik_cut(x)))

    parser = parser.drop(columns=['file name,'])

    parser = parser.merge(right=ticker, how='left', on='cik')
    parser = parser[['% negative,', 'cik', 'filingdate']]
    parser = parser.drop_duplicates()
    return parser


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
        if (i+1) % 10 == 0:
            print("{} files have been merged with returns".format(i+1))
    data.to_csv('./return_data.csv', index=False)
    return data


def get_result(ret_data):

    def quantile_calc(x, _quantiles=5):
        return pd.qcut(x, _quantiles, labels=False) + 1

    grouped_data = ret_data.copy()
    grouped_data = grouped_data.dropna()
    grouped_data['master_group'] = quantile_calc(grouped_data['master %negative'])
    grouped_data['harvard_group'] = quantile_calc(grouped_data['harvard %negative'])
    grouped_data['excessret'] = grouped_data['excessret']*100

    master_result = grouped_data[['master_group', 'excessret']].groupby('master_group').agg({'excessret': 'median'})
    harvard_result = grouped_data[['harvard_group', 'excessret']].groupby('harvard_group').agg({'excessret': 'median'})
    master_result.index = ['Low', '2', '3', '4', 'High']
    harvard_result.index = ['Low', '2', '3', '4', 'High']

    return master_result, harvard_result


def compare_plot(master_result, harvard_result, name):
    plt.figure(figsize=(8, 4))
    _ = plt.plot(master_result, 'go-', label='Fin_Neg')
    _ = plt.plot(harvard_result, 'bo-', label='Harvard_Neg')
    _ = plt.xlabel('Quintile(based on proportion of negative words)')
    _ = plt.ylabel('Median Filing Period Excess Return(%)')
    _ = plt.legend(loc='best')
    _ = plt.savefig(name + '_result.png')


if __name__ == '__main__':
    master_dic = pd.read_csv('LoughranMcDonald_MasterDictionary_2018.csv')
    master_neg_list = list(master_dic['Word'][master_dic['Negative'] > 0])
    harvard_dic = pd.read_csv('Harvard_Dictionary.csv')
    harvard_neg_list = list(harvard_dic['Entry'][harvard_dic['Negativ'] == 'Negativ'])

    print('Getting Parser Data...')
    master_data = clean_parser('Parser.csv')
    harvard_data = clean_parser('Parser_Harvard.csv')
    
    ticker = pd.read_csv('./ticker.txt', delimiter='\t', header=None, index_col=0)

    master_data = master_data.rename(columns={'% negative,': 'master %negative'})
    harvard_data = harvard_data.rename(columns={'% negative,': 'harvard %negative'})
    data = master_data.merge(right=harvard_data, on=['cik', 'filingdate'], how='inner')
  
    idf_weight = pd.read_csv('idf_weight.csv')
    idf_weight_hd = pd.read_csv('idf_weight_harvard.csv')
    #parser = pd.read_csv('Parser.csv')
    #parser_hd = pd.read_csv('Parser_Harvard.csv')
    idf_weight['%word'] = idf_weight.apply(lambda x: x.sum(), axis = 1)
    idf_weight['%neg'] = idf_weight[master_neg_list].apply(lambda x: x.sum(), axis = 1)   
    idf_weight_new = idf_weight[['%word','%neg']]
    idf_weight_new['%negative'] = idf_weight_new['%neg'] / idf_weight_new['%word'] 
    
    idf_weight_hd['%word'] = idf_weight_hd.apply(lambda x: x.sum(), axis = 1)
    idf_weight_hd['%neg'] = idf_weight_hd[[i for i in harvard_neg_list if i in idf_weight_hd.columns]].apply(lambda x: x.sum(), axis = 1)
    idf_weight_new_hd = idf_weight_hd[['%word','%neg']]
    idf_weight_new_hd['%negative'] = idf_weight_new_hd['%neg'] / idf_weight_new_hd['%word'] 
    

    print("Getting Return Data...")
    ret_data = merge_return(data)

    print('Getting Result...')
    master_result, harvard_result = get_result(ret_data)
    
    master_data_idf = idf_weight_new[['%negative']].rename(columns={'%negative': 'master %negative'})
    harvard_data_idf = idf_weight_new_hd[['%negative']].rename(columns={'%negative': 'harvard %negative'})
    result_idf = ret_data[['excessret']].join(master_data_idf)
    result_idf = result_idf.join(harvard_data_idf)
    master_result_idf, harvard_result_idf = get_result(result_idf)
    
    compare_plot(master_result, harvard_result, 'proportion')
    compare_plot(master_result_idf, harvard_result_idf, 'TD-idf')
    






















