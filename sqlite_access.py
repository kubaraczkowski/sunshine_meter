""" module for providing access to the brightness database, stored in sqlite3
"""


import sqlite3
import datetime
import logging
import json
import os
import pytz
from collections import deque

DB_FILE = os.path.join(os.path.dirname(__file__), 'brightness.db')

tz = pytz.timezone('Europe/Brussels')

def simplemovingaverage(period):
    assert period == int(period) and period > 0, "Period must be an integer >0"
 
    av = {'summ':0.0, 'n':0.0}
    av['values'] = deque([0.0] * period)     # old value queue
 
    def sma(x):
        av['values'].append(x)
        av['summ'] += x - av['values'].popleft()
        av['n'] = min(av['n']+1, period)
        return av['summ'] /av['n'] 
 
    return sma

def create_db():
    """ creates database DB_FILE with table sunshine with fields: timestamp, filename, brightness
    """
    conn = sqlite3.connect(DB_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute(''' CREATE TABLE IF NOT EXISTS sunshine
                    (ts timestamp, filename text, brightness real) ''')

def append(filename,brightness,dtime):
    """ adds entry to db. the entry parameters are: filename, timestamp, brightness
    """
    conn = sqlite3.connect(DB_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute(''' INSERT INTO sunshine (ts,filename,brightness)
                VALUES (?,?,?)''',(dtime,filename,brightness))


def query(start,stop,step=None,hour=None):
    """ retrieves from the db the filenames, timestamps and brightness from selected start to stop date (datetime objects) with given step between frames. E.g. if frames are taken every hour, then step = 12 means every half-day. If hour is given, then only given hour(s) are taken. In this case step goes over hour-specific entires. E.g. if hour=12 only noon pictures are queried and step=2 means results are given every 2nd day.
    """
    conn = sqlite3.connect(DB_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row

    params = ()
    main_code = ''' SELECT * FROM sunshine
        WHERE (julianday(ts) between julianday(?) AND julianday(?))'''
    params_main = (start,stop)

    query_code = main_code
    params = params_main
    if hour:
        hour_code = ''' AND abs((julianday(ts)-julianday(?))-round(julianday(ts)-julianday(?)))<0.05/24.0'''
        params_hour = ('%d:00'%hour,)*2
        query_code += hour_code
        params += params_hour
    if step:
        step_code = ''' AND (rowid - (SELECT rowid FROM sunshine
            ORDER BY ts LIMIT 1 )) % ?'''
        params_step = (step,)
        query_code += step_code
        params += params_step

    logging.debug(query_code)
    logging.debug(params)
    with conn:
        res = conn.execute(query_code,params)
    return res.fetchall()


def query_last_ndays(ndays=30,hour=None,step=None):
    """ simplified query where you can ask for the last x days at specific hour
    """
    stop = datetime.datetime.now()
    start = stop - datetime.timedelta(days=ndays)
    return query(start=start,stop=stop,hour=hour,step=step)

# json support
class SunshineJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, sqlite3.Row):
            d = {}
            d.update(obj)
            d['ts'] = d['ts'].isoformat()
            return d
        else:
            return super(SunshineJSONEncoder, self).default(obj)

def query_json(start,stop,step=None,hour=None):
    raw_data = query(start,stop,step,hour)
    return json.dumps(raw_data, cls=SunshineJSONEncoder)

class SunshineJSONEncoder_gcharts(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return  'Date(%s)'%obj.strftime('%Y,%m,%d,%H,%M,%S')
        elif isinstance(obj, sqlite3.Row):
            d = {}
            d.update(obj)
            d['ts'] = 'Date(%s)'%obj.strftime('%Y,%m,%d,%H,%M,%S')
            return d
        else:
            return super(SunshineJSONEncoder, self).default(obj)

def query_google_charts_json(start,stop,step=None,hour=None):
    raw_data = query(start,stop,step,hour)
    cols = []
    cols.append({'id':'ts','label':'date','type':'datetime'})
    cols.append({'id':'br','label':'brightness','type':'number'})
    cols.append({'id':'br','label':'average','type':'number'})

    rows = []
    aver = simplemovingaverage(12)
    [rows.append({'c':[{'v':x['ts']},{'v':x['brightness']},{'v':aver(x['brightness'])}]}) for x in raw_data]
    data = {'cols':cols,'rows':rows}
    return json.dumps(data, cls=SunshineJSONEncoder_gcharts)
