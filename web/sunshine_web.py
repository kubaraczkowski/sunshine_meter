from bottle import route,run,template,static_file
import sys
sys.path.append('..')
import sqlite_access
import datetime


@route('/')
def index():
    return template('index.html')

@route('/get_data/<hour:int>/<days:int>')
def get_data(hour=12,days=365):
    stop = datetime.datetime.now()
    start = stop - datetime.timedelta(days=days)
    return sqlite_access.query_google_charts_json(start,stop,hour=hour)

@route('/put/<user>/<choice>')
def add_to_db(user,choice):
	pass


run(reloader=True,debug=True)


