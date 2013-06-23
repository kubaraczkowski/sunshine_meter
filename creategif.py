import os
import subprocess
import logging

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
    gifsicle_delete_frame0 = 'gifsicle {output} --delay=10 --loop -O2 --colors 256 --conserve-memory --delete "#0" -o {output}'

    files = [x for x in files if x is not None]
    files = [x for x in files if x is not '']

    # convert files to gif
    logging.debug('converting files to gif')
    for f in files:
        if not os.path.isfile('%s.gif'%f):
            subprocess.call(convert.format(f=f),shell=True)
            logging.debug('converted: ' + f)

    # run gifsicle to create animation
    files = ' '.join([f+'.gif' for f in files])
    logging.debug('files to be joined in gif: ' + files)

    # first check numbers of frames in the output_filename
    if os.path.exists(output_filename):
        try:
            in_gif = int(subprocess.check_output(gifsicle_check_noframes.format(output=output_filename),shell=True).split()[2])
        except IndexError:
            logging.debug('ui, something wrong with the gif file. recreate completely')
            in_gif = 0
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
