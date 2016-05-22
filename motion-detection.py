#!/usr/bin/python

from picamera.array import PiRGBArray
from picamera import PiCamera
from datetime import datetime
import sqlite3
import time
import cv2
import params
import qhue

# init hue bridge connection
bridge = qhue.Bridge(params.hue_bridge_ip, params.hue_username)

# init database connection
conn = sqlite3.connect(params.database_path)
cur = conn.cursor()
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.5)
min_area = 1000
params.blend_rate = 0.1

# initialize the first frame in the video stream
firstFrame = None
prevGamma = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image
    image = frame.array

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    (gamma, _, _, _) = cv2.mean(gray)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        rawCapture.truncate(0)
        prevGamma = gamma * params.blend_rate + prevGamma * (1 - params.blend_rate)
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

    if hit_boxes > 0 and gamma > (1 - params.blend_rate) * prevGamma:
        # make sure phone is not here
        cur.execute('select is_available from %s\
                     where timestamp < datetime(\'now\', \'-%s minutes\')\
                     and mac = ?\
                     order by timestamp desc limit 1' % (params.table_name, params.phone_timeout_minutes),
                    (params.phone_mac, ))

        (is_available, ) = cur.next()

        if not is_available:
            bridge.groups[0].action(scene=params.wake_up_scene)
            cv2.imwrite("%s/%s.jpg" % (params.photo_capture_directory, datetime.now()), image)
    
    # slowly blend in current image onto background
    # FIXME: do it more slowly when motion is detected?
    firstFrame = cv2.addWeighted(firstFrame, 1 - params.blend_rate, gray, params.blend_rate, 0)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    prevGamma = gamma * params.blend_rate + prevGamma * (1 - params.blend_rate)
