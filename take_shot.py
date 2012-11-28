import cv2.cv as cv
import numpy
import pylab

CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4


camera = cv.CaptureFromCAM(0)
cv.SetCaptureProperty(camera, CV_CAP_PROP_FRAME_WIDTH, 1280)
cv.SetCaptureProperty(camera, CV_CAP_PROP_FRAME_HEIGHT, 720)

def get_image(filename=None):
    im = cv.QueryFrame(camera)

    #save file
    if filename:
        cv.SaveImage(filename,im)
    
    # take greyscale and compute RMS value
    im2 = cv.CreateImage(cv.GetSize(im),cv.IPL_DEPTH_32F,3)
    cv.Convert(im,im2)
    gray = cv.CreateImage(cv.GetSize(im),cv.IPL_DEPTH_32F,1)
    cv.CvtColor(im2,gray,cv.CV_RGB2GRAY)
    gray_mat = cv.GetMat(gray)
    img = numpy.asarray(gray_mat)

    power = numpy.sqrt(numpy.mean(img**2))

    #del(camera)
    del im, im2, gray, img, gray_mat

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
    ax.relim()
    ax.autoscale()
    fig.canvas.draw()
    

