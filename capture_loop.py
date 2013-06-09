""" Main loop for capturing picture (+brightness) every hour and storing it
in the ./pics folder. The timestamp is saved in the file name. Sqlite database stores the timestamp, brightness, filename(for easier tracking).
If time == midnight, a GIF animation is made from the last 24*30 files (one month)
"""

import datetime
from time import sleep
import subprocess
import os
import glob
import logging

import take_shot
import sqlite_access

DIR_PREFIX = './pics'

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

    

def create_animation(files,output_filename,noframes=None):
    """ Uses gifsicle to create animation. The parameters are hardcoded for the moment. First the files are converted using imagemagick's convert.
    """
    if not noframes:
        noframes = 30*24 # 30 days of 24 hours
    # subprocess templates
    convert = "convert -resize 50% {f} {f}.gif"
    gifsicle = "gifsicle --delay=10 --loop -O2 --colors 256 --conserve-memory {files} > {output}"
    gifsicle_check_noframes = "gifsicle --info {output} | head -n 1"
    gifsicle_append = "gifsicle {output} --delay=10 --loop -O2 --colors 256 --conserve-memory --append {what} -o {output}"
    gifsicle_delete_frame0 = 'gifsicle {output} --delay=10 --loop -O2 --colors 256 --corserve-memory --delete "#0" -o {output}'

    # convert files to gif
    logging.debug('converting files to gif')
    for f in files:
        if not os.path.isfile(f+'.gif'):
            subprocess.call(convert.format(f=f),shell=True)
            logging.debug('converted: ' + f)

    # run gifsicle to create animation
    files = ' '.join([f+'.gif' for f in files])
    logging.debug('files to be joined in gif: ' + files)

    # first check numbers of frames in the output_filename
    if os.path.exists(output_filename):
        in_gif = int(subprocess.check_output(gifsicle_check_noframes.format(output=output_filename),shell=True).split()[2])
        logging.debug('no. frames in existing gif: %d'%in_gif)
    else:
        in_gif = 0 

    if in_gif == 0: # no file
        # recreate file with all gifs
        logging.debug('no frames in file. recreating with all files')
        subprocess.call(gifsicle.format(files=files,output=output_filename),shell=True)
    else:
        if in_gif > noframes:
    	    # too many frames already. remove the first one
            logging.debug('too many frames in output file - removing first frame')
            subprocess.call(gifsicle_delete_frame0.format(output=output_filename),shell=True)
            logging.debug('removed...')
        # append the newest filename.gif to the file
        logging.debug('appending new frames to the output file')
        logging.debug('to be appended: %s'%files.split()[-1])
        subprocess.call(gifsicle_append.format(what="%s"%files.split()[-1],output=output_filename),shell=True)

        in_gif = int(subprocess.check_output(gifsicle_check_noframes.format(output=output_filename),shell=True).split()[2])
        logging.debug('no. frames in output file after append: %d'%in_gif)




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
        (brightness,written_file) = take_shot.get_image(camera,filename)
        logging.debug('completed shot')

        logging.debug('writing to db')
        sqlite_access.append(written_file,brightness,dtime)

        logging.debug('creating animation')
        logging.debug('getting files to be processed')
        files = []
        files = [f['filename'] for f in sqlite_access.query_last_ndays(ndays=1)]
        logging.debug(files)

        create_animation(files,'./animations/out.gif')
        logging.info("Created animation")

        logging.debug("cleaning up")
        cleanup_gifs(days_limit=2)
        sleep(10*60)

