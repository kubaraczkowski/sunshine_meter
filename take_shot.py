import cv2.cv as cv
import numpy
import pylab

CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4



def get_image(filename=None):
    camera = cv.CaptureFromCAM(0)
    cv.SetCaptureProperty(camera, CV_CAP_PROP_FRAME_WIDTH, 1280)
    cv.SetCaptureProperty(camera, CV_CAP_PROP_FRAME_HEIGHT, 720)
    im = cv.QueryFrame(camera)

    #save file
    if filename:
        cv.SaveImage(filename,im)
    
    # take greyscale and compute RMS value
    gray = cv.CreateImage(cv.GetSize(im),8,1)
    cv.CvtColor(im,gray,cv.CV_RGB2GRAY)
    gray_mat = cv.GetMat(gray)
    img = numpy.asarray(gray_mat)

    power = numpy.sqrt(numpy.mean(img**2))

    del(camera)

    return power

pylab.ion()
fig = pylab.figure()
ax = fig.add_subplot(111)

p = []
p.append(get_image())
ix = []
ix.append(1)
line1, = ax.plot(ix,p,'o-')

while True:
    p.append(get_image())
    print p[-1]
    ix.append(ix[-1]+1)
    line1.set_data(ix,p)
    ax.autoscale()
    fig.canvas.draw()
    

