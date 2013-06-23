""" Main loop for capturing picture (+brightness) every hour and storing it
in the ./pics folder. The timestamp is saved in the file name. Sqlite database stores the timestamp, brightness, filename(for easier tracking).
"""

import datetime
from time import sleep
import os
import glob
import logging

import take_shot
import sqlite_access
from memory import memory
import creategif

DIR_PREFIX = './pics'
GIF_HOURS = [5, 7, 9,10,11, 12,13,14, 15,16, 17,18, 19, 21]

def time_stamped(fname, fmt='%Y-%m-%d-%H-%M-%S_{fname}'):
    """ returns standardized filename for photo captures
    """
    dt = datetime.datetime.now()
    return (dt.strftime(fmt).format(fname=fname),dt)


def datetime_from_filename(fname):
    """ computes back (from time_stamped) the datetime of a file.
        Used for cleaning up
    """
    return datetime.datetime.strptime(os.path.split(fname.split("_")[0])[-1],'%Y-%m-%d-%H-%M-%S')


def is_file_to_old(fname,days_limit=30):
    """ checks if given file name suggest that file is older than 30 days. If yes, it can be removed.
        Used for cleaning up gif files
    """
    if (datetime_from_filename(fname) - datetime.datetime.now()).days + days_limit > 0:
        return False
    else:
        return True


def cleanup_gifs(days_limit=30):
    for fname in glob.glob(os.path.join(DIR_PREFIX,'*.gif')):
        if is_file_to_old(fname,days_limit):
            os.remove(fname)


if __name__=="__main__":
    logging.basicConfig(filename='sunshine.log',level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(console)
    logging.info('starting sunshine meter')

    logging.debug('init camera')
    camera = take_shot.init_camera()

    logging.debug('create or open database')
    sqlite_access.create_db()

    logging.debug('entering main loop')
    files = []
    while True:
        filename,dtime = time_stamped('home')
        logging.info(filename)

        logging.debug('taking shot')
        if dtime.hour in GIF_HOURS:
            (brightness,written_file) = take_shot.get_image(camera,filename)
        else:
            (brightness,written_file) = take_shot.get_image(camera,False)
        logging.debug('completed shot')

        logging.debug('writing to db')
        sqlite_access.append(written_file,brightness,dtime)

        for hour in GIF_HOURS:
            if dtime.hour == hour and dtime.minute == 0:
                logging.debug('creating animation')
                logging.debug('getting files to be processed for hour %d'%hour)
                files = []
                files = [f['filename'] for f in sqlite_access.query_last_ndays(ndays=30, hour=hour)]
                logging.debug(files)

                creategif.create_animation(files,'./animations/sunshine_%dh.gif'%hour)
                logging.info("Created animation for hour %d"%hour)

        logging.debug("cleaning up")
        cleanup_gifs(days_limit=31)
        logging.debug("memory usage: %.1fMB"%memory())

        # check when is the next (minute/hour), set sleep accordingly
        delay = (5- dtime.minute%5 -1)*60 + 60 - dtime.second
        logging.debug("delay till next capture %d seconds"%delay)
        sleep(delay)

