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
# User defined output file
OUTPUT_FILE = 'idf_weight.csv'

lm_dictionary = LM.load_masterdictionary(MASTER_DICTIONARY_FILE, True)
# Setup output
OUTPUT_FIELDS = list(lm_dictionary.keys())
parser_data = pd.read_csv('Parser.csv')

def get_idf_data(doc):
    tf_ij = np.zeros(len(OUTPUT_FIELDS))   
    tokens = re.findall('\w+', doc)  # Note that \w+ splits hyphenated words
    for token in tokens:
        if not token.isdigit() and len(token) > 1 and token in lm_dictionary:
            if lm_dictionary[token].negative:
                tf_ij[OUTPUT_FIELDS.index(token)] += 1
    
    tf_ij = 1 + np.log(tf_ij)
    tf_ij[np.isinf(tf_ij)] = 0
    return tf_ij


def main():   
    file_list = glob.glob(TARGET_FILES)    
    tf_idf = pd.DataFrame(index = parser_data.index, columns = OUTPUT_FIELDS)
    N = 290
    i = 0
    for file in file_list:
        print(file)
        with open(file, 'r', encoding='UTF-8', errors='ignore') as f_in:
            doc = f_in.read()
        doc_len = len(doc)
        doc = re.sub('(May|MAY)', ' ', doc)  # drop all May month references
        doc = doc.upper()  # for this parse caps aren't informative so shift

        tf_ij = get_idf_data(doc)
        tf_idf.iloc[i,:] = tf_ij / (1 + np.log(parser_data.iloc[i]['number of words,']))
        i += 1
        
    temp = list(np.log(N / (tf_idf > 0).sum(axis = 0)))
    tf_idf *= temp
    tf_idf.to_csv(OUTPUT_FILE)
        

if __name__ == '__main__':
    print('\n' + time.strftime('%c') + '\nGet_tf_weight.py\n')
    main()
    print('\n' + time.strftime('%c') + '\nNormal termination.')