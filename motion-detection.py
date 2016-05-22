# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from datetime import datetime
import time
import cv2
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.5)
min_area = 1000

# initialize the first frame in the video stream
firstFrame = None
prevGamma = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image
    image = frame.array

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    (gamma, _, _, _) = cv2.mean(gray)

    print gamma

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        rawCapture.truncate(0)
        prevGamma = gamma * 0.1 + prevGamma * 0.9
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 35, 255, cv2.THRESH_BINARY)[1]
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
    hit_boxes = 0

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < min_area:
            continue
 
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        hit_boxes += 1

    if hit_boxes > 0 and gamma > 0.9 * prevGamma:
        print "Wrote to test-out.jpg"
        cv2.imwrite("photo-capture/%s.jpg" % datetime.now(), image)
    
    # slowly blend in current image onto background
    # FIXME: do it more slowly when motion is detected?
    firstFrame = cv2.addWeighted(firstFrame, 0.9, gray, 0.1, 0)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    prevGamma = gamma * 0.1 + prevGamma * 0.9
