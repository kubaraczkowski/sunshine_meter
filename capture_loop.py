""" Main loop for capturing picture (+brightness) every hour and storing it
in the ./pics folder. The timestamp is saved in the file name. Sqlite database stores the timestamp, brightness, filename(for easier tracking).
If time == midnight, a GIF animation is made from the last 24*30 files (one month)
"""

import datetime
from time import sleep
import subprocess
import os
import glob

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
    convert = "convert -resize 50% {f} {f}.gif"
    gifsicle = "gifsicle --delay=10 --loop -O2 --colors 256 --conserve-memory {files} > {output}"
    gifsicle_check_noframes = "gifsicle --info | head -n 1"
    gifsicle_append = "gifsicle --delay=10 --loop -O2 --colors 256 --corserve-memory --append {what} -o {output}"
    gifsicle_delete_frame0 = 'gifsicle --delay=10 --loop -O2 --colors 256 --corserve-memory --delete "#0" -o {output}'

    # convert files to gif
    for f in files:
        if not os.path.isfile(f+'.gif'):
            subprocess.call(convert.format(f=f),shell=True)
    # run gifsicle to create animation
    files = ' '.join([f+'.gif' for f in files])
    # first check numbers of frames in the output_filename
    in_gif=int(subprocess.check_output(gifsicle_check_noframes,shell=True).split()[2])
    if in_gif > noframes:
	# too many frames already. remove the first one
        subprocess.call(gifsicle_delete_frame0.format(output=output_filename),shell=True)
    # append the newest filename.gif to the file
    subprocess.call(gifsicle_append.format(what="%s.gif"%files[-1],output=output_filename),shell=True)




if __name__=="__main__":
    camera = take_shot.init_camera()
    sqlite_access.create_db()

    files = []
    while True:
        filename,dtime = time_stamped('home')
        print filename
        (brightness,written_file) = take_shot.get_image(camera,filename)
        sqlite_access.append(written_file,brightness,dtime)

        files = []
        files = [f['filename'] for f in sqlite_access.query_last_ndays(ndays=1)]
        create_animation(files,'./animations/out.gif')
        print("Created animation")

        cleanup_gifs(days_limit=2)
        sleep(10*60)

