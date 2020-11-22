#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 03:35:59 2020

@author: yi
"""

import csv
import glob
import re
import string
import sys
import time
import Load_MasterDictionary as LM
import pandas as pd
import numpy as np
# User defined directory for files to be parsed
TARGET_FILES = r'./files/*.*'
# User defined file pointer to LM dictionary
MASTER_DICTIONARY_FILE = r'./LoughranMcDonald_MasterDictionary_2018.csv'
# User defined file pointer to Harvard dictionary
HARVARD_DICTIONARY_FILE = r'./Harvard_Dictionary.xls'
# User defined output file1
OUTPUT_FILE1 = 'idf_weight_lm.csv'
# User defined output file1
OUTPUT_FILE2 = 'idf_weight_hv.csv'

lm_dictionary = LM.load_masterdictionary(MASTER_DICTIONARY_FILE, True)
hv_dictionary = pd.read_excel(HARVARD_DICTIONARY_FILE,skiprows = [1])
#change the alphanum to alpha and drop duplicates
hv_dictionary['Entry'] = hv_dictionary['Entry'].apply(lambda s: ''.join(x for x in s if x.isalpha()))
hv_dictionary = hv_dictionary.drop_duplicates(subset=['Entry'], keep='first')
hv = hv_dictionary.loc[hv_dictionary['Negativ'] == 'Negativ',['Entry','Negativ']]
negativefields = list(hv['Entry'].values)
# Setup output
OUTPUT_FIELDS1 = list(lm_dictionary.keys())
OUTPUT_FIELDS2 = list(hv_dictionary['Entry'].values)
parser_data = pd.read_csv('Parser.csv')

def get_idf_data(doc):
    tf_ij = np.zeros(len(OUTPUT_FIELDS1))   
    tf_ij2 = np.zeros(len(OUTPUT_FIELDS2))   
    tokens = re.findall('\w+', doc)  # Note that \w+ splits hyphenated words
    num = 0  #number of words
    negnum = 0  #number of negative words
    for token in tokens:
        if not token.isdigit() and len(token) > 1:
            if token in lm_dictionary and lm_dictionary[token].negative:
                tf_ij[OUTPUT_FIELDS1.index(token)] += 1
            elif token in OUTPUT_FIELDS2:
                num += 1
                if token in negativefields:
                    negnum += 1
                    tf_ij2[OUTPUT_FIELDS2.index(token)] += 1
    
    tf_ij = 1 + np.log(tf_ij)
    tf_ij[np.isinf(tf_ij)] = 0
    
    tf_ij2 = 1 + np.log(tf_ij2)
    tf_ij2[np.isinf(tf_ij2)] = 0
    return tf_ij,tf_ij2, num, negnum
'''
def get_idf_data2(doc):
    tf_ij2 = np.zeros(len(OUTPUT_FIELDS2))   
    tokens = re.findall('\w+', doc)  # Note that \w+ splits hyphenated words
    num = 0  #number of words
    negnum = 0  #number of negative words
    for token in tokens:
        
        if not token.isdigit() and len(token) > 1 and token in hv_dictionary['Entry'].values:
            num += 1
            if token in hv['Entry'].values:
                negnum += 1
                tf_ij2[OUTPUT_FIELDS2.index(token)] += 1
    
    tf_ij2 = 1 + np.log(tf_ij2)
    tf_ij2[np.isinf(tf_ij2)] = 0
    return tf_ij2, num, negnum
'''  


def main():   
    file_list = glob.glob(TARGET_FILES)
    tf_idf = pd.DataFrame(index = parser_data.index, columns = OUTPUT_FIELDS1)
    tf_idf2 = pd.DataFrame(index = parser_data.index, columns = OUTPUT_FIELDS2)
    N = len(file_list)
    i = 0
    numlist = []
    negnumlist = []
    for file in file_list:
        print(file)
        with open(file, 'r', encoding='UTF-8', errors='ignore') as f_in:
            doc = f_in.read()
        doc_len = len(doc)
        doc = re.sub('(May|MAY)', ' ', doc)  # drop all May month references
        doc = doc.upper()  # for this parse caps aren't informative so shift

        tf_ij, tf_ij2, num, negnum = get_idf_data(doc)
        #tf_ij2, num, negnum = get_idf_data2(doc)
        numlist.append(num)
        negnumlist.append(negnum)
        tf_idf.iloc[i,:] = tf_ij / (1 + np.log(parser_data.iloc[i]['number of words,']))
        tf_idf2.iloc[i,:] = tf_ij2/ (1 + np.log(num))
        i += 1
        print(tf_idf2)
        print(numlist)
        print(negnumlist)
        
    temp = list(np.log(N / (tf_idf > 0).sum(axis = 0)))
    temp2 = list(np.log(N / (tf_idf2 > 0).sum(axis = 0)))
    tf_idf *= temp
    tf_idf2 *= temp2
    tf_idf2['number of words'] = numlist
    tf_idf2['number of negative words'] = negnumlist
    tf_idf.to_csv(OUTPUT_FILE1)
    tf_idf2.to_csv(OUTPUT_FILE2) 

if __name__ == '__main__':
    print('\n' + time.strftime('%c') + '\nGet_tf_weight.py\n')
    main()
    print('\n' + time.strftime('%c') + '\nNormal termination.')