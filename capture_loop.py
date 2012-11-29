""" Main loop for capturing picture (+brightness) every hour and storing it
in the ./pics folder. The timestamp is saved in the file name. Sqlite database stores the timestamp, brightness, filename(for easier tracking).
If time == midnight, a GIF animation is made from the last 24*30 files (one month)
"""

import datetime
from time import sleep
import take_shot

def time_stamped(fname, fmt='%Y-%m-%d-%H-%M-%S_{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

camera = take_shot.init_camera()

while True:
    filename = time_stamped('home')
    print filename
    brightness = take_shot.get_image(camera,filename)
    sleep(5)
