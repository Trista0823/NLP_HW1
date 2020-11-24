"""
Created on Tue Nov 17 03:35:59 2020

@author: Mengyao
"""

import time


def load_harvard_dictionary(file_path, print_flag=False, f_log=None, get_other=False):
    _harvard_dictionary = {}
    _sentiment_categories = ['negative']
    # Load slightly modified nltk stopwords.  I do not use nltk import to avoid versioning errors.
    # Dropped from nltk: A, I, S, T, DON, WILL, AGAINST
    # Added: AMONG,
    _stopwords = ['ME', 'MY', 'MYSELF', 'WE', 'OUR', 'OURS', 'OURSELVES', 'YOU', 'YOUR', 'YOURS',
                       'YOURSELF', 'YOURSELVES', 'HE', 'HIM', 'HIS', 'HIMSELF', 'SHE', 'HER', 'HERS', 'HERSELF',
                       'IT', 'ITS', 'ITSELF', 'THEY', 'THEM', 'THEIR', 'THEIRS', 'THEMSELVES', 'WHAT', 'WHICH',
                       'WHO', 'WHOM', 'THIS', 'THAT', 'THESE', 'THOSE', 'AM', 'IS', 'ARE', 'WAS', 'WERE', 'BE',
                       'BEEN', 'BEING', 'HAVE', 'HAS', 'HAD', 'HAVING', 'DO', 'DOES', 'DID', 'DOING', 'AN',
                       'THE', 'AND', 'BUT', 'IF', 'OR', 'BECAUSE', 'AS', 'UNTIL', 'WHILE', 'OF', 'AT', 'BY',
                       'FOR', 'WITH', 'ABOUT', 'BETWEEN', 'INTO', 'THROUGH', 'DURING', 'BEFORE',
                       'AFTER', 'ABOVE', 'BELOW', 'TO', 'FROM', 'UP', 'DOWN', 'IN', 'OUT', 'ON', 'OFF', 'OVER',
                       'UNDER', 'AGAIN', 'FURTHER', 'THEN', 'ONCE', 'HERE', 'THERE', 'WHEN', 'WHERE', 'WHY',
                       'HOW', 'ALL', 'ANY', 'BOTH', 'EACH', 'FEW', 'MORE', 'MOST', 'OTHER', 'SOME', 'SUCH',
                       'NO', 'NOR', 'NOT', 'ONLY', 'OWN', 'SAME', 'SO', 'THAN', 'TOO', 'VERY', 'CAN',
                       'JUST', 'SHOULD', 'NOW']

    with open(file_path) as f:
        _md_header = f.readline()
        for line in f:
            cols = line.split(',')
            _harvard_dictionary[cols[0]] = HavardDictionary(cols, _stopwords)
            if len(_harvard_dictionary) % 5000 == 0 and print_flag:
                print('\r ...Loading Harvard Dictionary' + ' {}'.format(len(_harvard_dictionary)), end='', flush=True)

    if print_flag:
        print('\r', end='')  # clear line
        print('\nHarvard Dictionary loaded from file: \n  ' + file_path)
        print('  {0:,} words loaded in harvard_dictionary.'.format(len(_harvard_dictionary)) + '\n')

    if f_log:
        try:
            f_log.write('\n\n  load_harvarddictionary log:')
            f_log.write('\n    Harvard Dictionary loaded from file: \n       ' + file_path)
            f_log.write('\n    {0:,} words loaded in harvard_dictionary.\n'.format(len(_harvard_dictionary)))
        except Exception as e:
            print('Log file in load_harvarddictionary is not available for writing')
            print('Error = {0}'.format(e))

    if get_other:
        return _harvard_dictionary, _md_header, _sentiment_categories, _stopwords
    else:
        return _harvard_dictionary


class HavardDictionary:
    def __init__(self, cols, _stopwords):
        self.word = cols[0].upper()
        self.source = cols[1]

        self.negative = cols[3]
        self.sentiment = {}
        self.sentiment['negative'] = bool(self.negative)

        if self.word in _stopwords:
            self.stopword = True
        else:
            self.stopword = False
        return


if __name__ == '__main__':
    # Full test program in /TextualAnalysis/TestPrograms/Test_Load_MasterDictionary.py
    print(time.strftime('%c') + '/n')
    md = (r'./Harvard_Dictionary.csv')
    harvard_dictionary, md_header, sentiment_categories, stopwords = load_harvard_dictionary(md, True, False, True)
    print(harvard_dictionary.keys())
    print('\n' + 'Normal termination.')
    print(time.strftime('%c') + '/n')