#!/usr/bin/python3
"""
    Utility programs for accessing SEC/EDGAR
    ND-SRAF / McDonald : 201606
    https.//sraf.nd.edu
"""
# ticker.txt from https://www.sec.gov/include/ticker.txt



def get_cik():
    import pandas as pd

    ticker = pd.read_csv('./ticker.txt', delimiter='\t', header=None)
    dow30 = pd.read_excel('./dow30_complete.xlsx', index_col=0)

    dow30 = dow30.loc[:,['from', 'thru', 'co_conm', 'co_tic']]
    dow30['thru'] = dow30['thru'].replace('.','20201116')
    dow30['co_tic'] = dow30['co_tic'].apply(lambda x: str.lower(x))
    ticker = ticker.rename(columns={0:'co_tic',1:'cik'})

    dow30 = dow30.merge(ticker, how='left', on='co_tic')

    dow30['start_y'] = dow30['from'].apply(lambda x: int(str(x)[:4]))
    dow30['end_y'] = dow30['thru'].apply(lambda x: int(str(x)[:4]))

    dow30['start_q'] = dow30['from'].apply(lambda x: (int(str(x)[4:6])-1)//3+1)
    dow30['end_q'] = dow30['thru'].apply(lambda x: (int(str(x)[4:6])-1)//3+1)

    dow30 = dow30.loc[:,['start_y', 'start_q', 'end_y', 'end_q', 'cik']]
    dow30 = dow30.set_index('cik').T.to_dict('list')
    return dow30


def download_masterindex(year, qtr, flag=False):
    # Download Master.idx from EDGAR
    # Loop accounts for temporary server/ISP issues
    # ND-SRAF / McDonald : 201606

    import time
    from urllib.request import urlopen
    from zipfile import ZipFile
    from io import BytesIO

    number_of_tries = 10
    sleep_time = 10  # Note sleep time accumulates according to err


    PARM_ROOT_PATH = 'https://www.sec.gov/Archives/edgar/full-index/'

    start = time.clock()  # Note: using clock time not CPU
    masterindex = []
    #  using the zip file is a little more complicated but orders of magnitude faster
    append_path = str(year) + '/QTR' + str(qtr) + '/master.zip'  # /master.idx => nonzip version
    sec_url = PARM_ROOT_PATH + append_path

    for i in range(1, number_of_tries + 1):
        try:
            zipfile = ZipFile(BytesIO(urlopen(sec_url).read()))
            records = zipfile.open('master.idx').read().decode('utf-8', 'ignore').splitlines()[10:]
#           records = urlopen(sec_url).read().decode('utf-8').splitlines()[10:] #  => nonzip version
            break
        except Exception as exc:
            if i == 1:
                print('\nError in download_masterindex')
            print('  {0}. _url:  {1}'.format(i, sec_url))

            print('  Warning: {0}  [{1}]'.format(str(exc), time.strfime('%c')))
            if '404' in str(exc):
                break
            if i == number_of_tries:
                return False
            print('     Retry in {0} seconds'.format(sleep_time))
            time.sleep(sleep_time)
            sleep_time += sleep_time


    # Load m.i. records into masterindex list

    dow30 = get_cik()
    for line in records:
        mir = MasterIndexRecord(line)
        if not mir.err and mir.cik in dow30:
            masterindex.append(mir)

            # if dow30[mir.cik][0]*10+dow30[mir.cik][1] <= year*10+qtr <= dow30[mir.cik][2]*10+dow30[mir.cik][3]:
            #     masterindex.append(mir)

    if flag:
        print('download_masterindex:  ' + str(year) + ':' + str(qtr) + ' | ' +
              'len() = {:,}'.format(len(masterindex)) + ' | Time = {0:.4f}'.format(time.clock() - start) +
              ' seconds')

    return masterindex


class MasterIndexRecord:
    def __init__(self, line):
        self.err = False
        parts = line.split('|')
        if len(parts) == 5:
            self.cik = int(parts[0])
            self.name = parts[1]
            self.form = parts[2]
            self.filingdate = int(parts[3].replace('-', ''))
            self.path = parts[4]
        else:
            self.err = True
        return


def edgar_server_not_available(flag=False):
    # routine to run download only when EDGAR server allows bulk download.
    # see:  https://www.sec.gov/edgar/searchedgar/ftpusers.htm
    # local time is converted to EST for check

    from datetime import datetime as dt
    import pytz
    import time

    SERVER_BGN = 21  # Server opens at 9:00PM EST
    SERVER_END = 6   # Server closes at 6:00AM EST

    # Get UTC time from local and convert to EST
    utc_dt = pytz.utc.localize(dt.utcnow())
    est_timezone = pytz.timezone('US/Eastern')
    est_dt = est_timezone.normalize(utc_dt.astimezone(est_timezone))

    if est_dt.hour >= SERVER_BGN or est_dt.hour < SERVER_END:
        return False
    else:
        if flag:
            print('\rSleeping: ' + str(dt.now()), end='', flush=True)
        time.sleep(600)  # Sleep for 10 minutes
        return True


