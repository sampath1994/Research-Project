import numpy as np
import cv2
import pybgs as bgs
from pathlib import Path
from timeit import default_timer as timer
from speed.track import update

algorithm = bgs.MultiLayer()
video_file = str(Path.cwd().parent / 'videos' / 'video03.avi')

BB_MIN_HEIGHT = 10
BB_MIN_WIDTH = 10
capture = cv2.VideoCapture(video_file)
while not capture.isOpened():
    capture = cv2.VideoCapture(video_file)
    cv2.waitKey(1000)
    print("Wait for the header")

#pos_frame = capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
#pos_frame = capture.get(cv2.CV_CAP_PROP_POS_FRAMES)
pos_frame = capture.get(1)

mask = cv2.imread('mask.jpg', cv2.IMREAD_GRAYSCALE)
rt, msk = cv2.threshold(mask, 30, 255, cv2.THRESH_BINARY)
global_bbs = []
next_id = 0
total_vehicles = 0
while True:
    flag, frame = capture.read()
    local_bbs = []
    if flag:
        start = timer()
        # cv2.imshow('video', frame)
        #pos_frame = capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        #pos_frame = capture.get(cv2.CV_CAP_PROP_POS_FRAMES)
        pos_frame = capture.get(1)
        #print str(pos_frame)+" frames"

        frame = cv2.bitwise_and(frame, frame, mask=msk)

        img_output = algorithm.apply(frame)
        img_bgmodel = algorithm.getBackgroundModel()

        img_output = cv2.dilate(img_output, None, iterations=3)  # 3
        img_output = cv2.erode(img_output, None, iterations=1)  # 1
        ############################################################# convex hull drawing
        im2, contours, hierarchy = cv2.findContours(img_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # hull = []
        # for i in range(len(contours)):
            # creating convex hull object for each contour
            # hull.append(cv2.convexHull(contours[i], False))

        # draw contours and hull points
        for i in range(len(contours)):
            color_contours = (0, 255, 0)  # green - color for contours
            color = (255, 0, 0)  # blue - color for convex hull
            cv2.drawContours(frame, contours, i, color, 1, 8)
            x, y, w, h = cv2.boundingRect(contours[i])
            if w > BB_MIN_WIDTH and h > BB_MIN_HEIGHT:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                local_bbs.append([x, y, w, h, -1, [], -1, 1])
        #############################################################
        next_id, updated_local_bbs = update(global_bbs, local_bbs, next_id)
        for bb in updated_local_bbs:
            cv2.putText(frame, str(bb[4]), (bb[0], bb[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            total_vehicles = total_vehicles + bb[7]
        cv2.putText(frame, str(total_vehicles), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        total_vehicles = 0
        global_bbs.append(updated_local_bbs)
        end = timer()
        print(int(1/(end-start)))  # This FPS represent processing power of algo. this isn't video FPS
        cv2.imshow('video', frame)
        cv2.imshow('img_output', img_output)
        cv2.imshow('img_bgmodel', img_bgmodel)

    else:
        #capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
        #capture.set(cv2.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
        #capture.set(1, pos_frame-1)
        #print "Frame is not ready"
        cv2.waitKey(1000)
        break

    if 0xFF & cv2.waitKey(10) == 27:
        break

    #if capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
    #if capture.get(cv2.CV_CAP_PROP_POS_FRAMES) == capture.get(cv2.CV_CAP_PROP_FRAME_COUNT):
    #if capture.get(1) == capture.get(cv2.CV_CAP_PROP_FRAME_COUNT):
    #break

cv2.destroyAllWindows()
