import csv
import glob
import re
import string
import sys
import time
# sys.path.append('D:\GD\Python\TextualAnalysis\Modules')  # Modify to identify path for custom modules
import Load_HarvardDictionary as LH

# User defined directory for files to be parsed
TARGET_FILES = r'./files/*.*'
# User defined file pointer to LM dictionary
HARVARD_DICTIONARY_FILE = r'./Harvard_Dictionary.csv'
# User defined output file
OUTPUT_FILE = r'./Parser_Harvard.csv'
# Setup output
OUTPUT_FIELDS = ['file name,', 'file size,', 'number of words,', '% negative,',
                 '# of alphabetic,', '# of digits,',
                 '# of numbers,', 'average word length,', 'vocabulary']

hv_dictionary = LH.load_harvard_dictionary(HARVARD_DICTIONARY_FILE, True)


def get_data(doc):
    vdictionary = {}
    _odata = [0] * len(OUTPUT_FIELDS)
    word_length = 0

    tokens = re.findall('\w+', doc)  # Note that \w+ splits hyphenated words
    for token in tokens:
        if not token.isdigit() and len(token) > 1 and token in hv_dictionary:
            _odata[2] += 1  # word count
            word_length += len(token)
            if token not in vdictionary:
                vdictionary[token] = 1
            if hv_dictionary[token].negative:
                _odata[3] += 1

    _odata[4] = len(re.findall('[A-Z]', doc))
    _odata[5] = len(re.findall('[0-9]', doc))
    # drop punctuation within numbers for number count
    doc = re.sub('(?!=[0-9])(\.|,)(?=[0-9])', '', doc)
    doc = doc.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
    _odata[6] = len(re.findall(r'\b[-+\(]?[$€£]?[-+(]?\d+\)?\b', doc))
    _odata[7] = word_length / _odata[2]
    _odata[8] = len(vdictionary)

    # Convert counts to %
    _odata[3] = (_odata[3] / _odata[2]) * 100
    # Vocabulary

    return _odata


def main():

    f_out = open(OUTPUT_FILE, 'w')
    wr = csv.writer(f_out, lineterminator='\n')
    wr.writerow(OUTPUT_FIELDS)

    file_list = glob.glob(TARGET_FILES)
    for file in file_list:
        print(file)
        with open(file, 'r', encoding='UTF-8', errors='ignore') as f_in:
            doc = f_in.read()
        doc_len = len(doc)
        doc = re.sub('(May|MAY)', ' ', doc)  # drop all May month references
        doc = doc.upper()  # for this parse caps aren't informative so shift

        output_data = get_data(doc)
        output_data[0] = file
        output_data[1] = doc_len
        wr.writerow(output_data)


if __name__ == '__main__':
    print('\n' + time.strftime('%c') + '\nHarvard_Parser.py\n')
    main()
    print('\n' + time.strftime('%c') + '\nNormal termination.')