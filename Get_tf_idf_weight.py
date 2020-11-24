#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 03:35:59 2020

@author: yi
"""

import glob
import re
import time
import Load_MasterDictionary as LM
import Load_HarvardDictionary as LH
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# User defined directory for files to be parsed
TARGET_FILES = r'./files/*.*'
# User defined file pointer to dictionaries
MASTER_DICTIONARY_FILE = r'./LoughranMcDonald_MasterDictionary_2018.csv'
HARVARD_DICTIONARY_FILE = r'./Harvard_Dictionary.csv'
# User defined output files
OUTPUT_FILE_MASTER = 'idf_weight.csv'
OUTPUT_FILE_HARVARD = 'idf_weight_harvard.csv'
# Parser files
PARSER_DATA_MASTER = pd.read_csv('Parser.csv')
PARSER_DATA_HARVARD = pd.read_csv('Parser_Harvard.csv')


def get_idf_data(doc, output_fields, dictionary):
    tf_ij = np.zeros(len(output_fields))
    tokens = re.findall('\w+', doc)  # Note that \w+ splits hyphenated words
    for token in tokens:
        if not token.isdigit() and len(token) > 1 and token in dictionary:
            tf_ij[output_fields.index(token)] += 1
            # if dictionary[token].negative:
                # tf_ij[output_fields.index(token)] += 1
    
    tf_ij = 1 + np.log(tf_ij)
    tf_ij[np.isinf(tf_ij)] = 0
    return tf_ij


def main(output_fields, dictionary, parser_data, output_file):
    file_list = glob.glob(TARGET_FILES)    
    tf_idf = pd.DataFrame(index=parser_data.index, columns=output_fields)
    N = 290
    i = 0
    for file in file_list:
        print(file)
        with open(file, 'r', encoding='UTF-8', errors='ignore') as f_in:
            doc = f_in.read()
        doc_len = len(doc)
        doc = re.sub('(May|MAY)', ' ', doc)  # drop all May month references
        doc = doc.upper()  # for this parse caps aren't informative so shift

        tf_ij = get_idf_data(doc, output_fields, dictionary)
        tf_idf.iloc[i, :] = tf_ij / (1 + np.log(parser_data.iloc[i]['number of words,']))
        i += 1
        
    temp = list(np.log(N / (tf_idf > 0).sum(axis=0)))
    tf_idf *= temp
    tf_idf.to_csv(output_file)
        

if __name__ == '__main__':
    MASTER = True
    HARVARD = True
    if MASTER:
        print('Getting tf-idf weight of master dictionary:')
        print('\n' + time.strftime('%c') + '\nGet_tf_weight.py\n')

        lm_dictionary = LM.load_masterdictionary(MASTER_DICTIONARY_FILE, True)
        OUTPUT_FIELDS_MASTER = list(lm_dictionary.keys())
        main(OUTPUT_FIELDS_MASTER, lm_dictionary, PARSER_DATA_MASTER, OUTPUT_FILE_MASTER)

        print('\n' + time.strftime('%c') + '\nNormal termination.')

    if HARVARD:
        print('Getting tf-idf weight of harvard dictionary:')
        print('\n' + time.strftime('%c') + '\nGet_tf_weight.py\n')

        lh_dictionary = LH.load_harvard_dictionary(HARVARD_DICTIONARY_FILE, True)
        OUTPUT_FIELDS_HARVARD = list(lh_dictionary.keys())
        main(OUTPUT_FIELDS_HARVARD, lh_dictionary, PARSER_DATA_HARVARD, OUTPUT_FILE_HARVARD)

        print('\n' + time.strftime('%c') + '\nNormal termination.')