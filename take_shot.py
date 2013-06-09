import cv2.cv as cv
import numpy
import os

CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4

DIR_PREFIX = './pics'
DATE_X = 850
DATE_Y = 680


def init_camera(rx=640,ry=480):
    setup_uvc_camera()
    camera = cv.CaptureFromCAM(0)
    # set camera properties
    cv.SetCaptureProperty(camera, CV_CAP_PROP_FRAME_WIDTH, rx)
    cv.SetCaptureProperty(camera, CV_CAP_PROP_FRAME_HEIGHT, ry)
    return camera

def setup_uvc_camera():
    command = 'uvcdynctrl -s '
    command += 'Brightness 0'
    os.system(command)
    command = 'uvcdynctrl -s '
    command += 'Contrast 13'
    os.system(command)
    command = 'uvcdynctrl -s '
    command += '"White Balance Temperature, Auto" 0'
    os.system(command)
    command = 'uvcdynctrl -s '
    command += '"White Balance Temperature" 6500'
    os.system(command)
    command = 'uvcdynctrl -s '
    command += '"Backlight Compensation" 0'
    os.system(command)
    command = 'uvcdynctrl -s '
    command += '"Exposure, Auto" 1'
    os.system(command)
    command = 'uvcdynctrl -s '
    command += '"Exposure (Absolute)" 300'
    os.system(command)
    command = 'uvcdynctrl -s '
    command += '"Exposure, Auto Priority" 0'
    os.system(command)

def get_image(camera,filename=None):
    im = cv.QueryFrame(camera)

    
    # take greyscale and compute RMS value
    im2 = cv.CreateImage(cv.GetSize(im),cv.IPL_DEPTH_32F,3)
    cv.Convert(im,im2)
    gray = cv.CreateImage(cv.GetSize(im),cv.IPL_DEPTH_32F,1)
    cv.CvtColor(im2,gray,cv.CV_RGB2GRAY)
    gray_mat = cv.GetMat(gray)
    img = numpy.asarray(gray_mat)

    power = numpy.sqrt(numpy.mean(img**2))

    #save file
    if filename:
        font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.8, 0.8, 0, 2, cv.CV_AA)
        cv.PutText(im,filename,(DATE_X,DATE_Y),font,cv.RGB(255,255,0))
        filename = os.path.join(DIR_PREFIX,filename+'.jpg')
        print filename
        cv.SaveImage(filename,im)

    #del(camera)
    del im, im2, gray, img, gray_mat, font

    return (power,filename)

if __name__ == '__main__':
    import pylab
    pylab.ion()
    fig = pylab.figure()
    ax = fig.add_subplot(111)

    p = []
    init_camera()
    p.append(get_image())
    ix = []
    ix.append(1)
    line1, = ax.plot(ix,p,'o-')

    while True:
        p.append(get_image())
        print p[-1]
        ix.append(ix[-1]+1)
        line1.set_data(ix,p)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        

