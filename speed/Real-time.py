import numpy as np
import cv2
import pybgs as bgs
from pathlib import Path
import pandas as pd
from timeit import default_timer as timer
from speed.track import update, get_vehicle_count_in_blob, count_and_speed, speed_by_ref_points, load_speed_coord
from fuzzy_decision.Decision import init_fuzzy_system, get_decision

algorithm = bgs.MultiLayer()
video_file = str(Path.cwd().parent / 'videos' / 'video03.avi')
speed_weight_file = str(Path.cwd().parent / 'weights.csv')

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
car_cascade = cv2.CascadeClassifier('cars.xml')
global_bbs = []
next_id = 0
total_vehicles = 0
frame_count = 0
frame_interval = 5  # speed and count calculated for each of this number of frames
avg_speed = 0
frame_rate = 60
df = pd.read_csv(speed_weight_file, delimiter=',', header=None)
wght = float(df[0].values)
bis = float(df[1].values)
real_car_length = 4  # put mean car length in meters
upper_dic = {}
lower_dic = {}
REF_SPEED_MODE = False
BOTH_CHANNEL = True
real_dis = 8  # real distance in Meters, between marked reference points
frame_thresh = 250  # clean dictionaries older than frame threshold
if REF_SPEED_MODE:
    upper_row, lower_row = load_speed_coord(str(Path.cwd() / 'screen-mark' / 'speed_markings.pkl'))

###########################################################################
from sort import *
from pedestrian.counter import get_roi_contour
from pedestrian.pedestrian_Detection import ped

camera = cv2.VideoCapture(str(Path.cwd().parent / 'videos' / 'pedestrians.avi'))
# camera.open("pedestrians.avi")
ped_cascade = cv2.CascadeClassifier(str(Path.cwd().parent / 'pedestrian' / 'cascade3.xml'))
frm_count = 0
# # create instance of SORT
mot_tracker = Sort()
cont = get_roi_contour(int(camera.get(4)), int(camera.get(3)))
pre_objs = []
current_objs = []
ped_count_in_roi = 0
wait_frame_count = 0
standing_thresh = 5
###########################################################################

sim = init_fuzzy_system()
requirement_threshold = 4

while True:
    flag, frame = capture.read()
    ##############################
    if BOTH_CHANNEL:
        if frame_count % 6 == 0:  # MOD value = Higher FPS / Lower FPS
            (grabbed, framez) = camera.read()
            ped_count_in_roi, frm_count, wait_frame_count = ped(framez, ped_cascade, current_objs, cont, frm_count, ped_count_in_roi, wait_frame_count, mot_tracker, standing_thresh)
    ##############################
    local_bbs = []
    if flag:
        start = timer()
        # cv2.imshow('video', frame)
        #pos_frame = capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        #pos_frame = capture.get(cv2.CV_CAP_PROP_POS_FRAMES)
        pos_frame = capture.get(1)
        #print str(pos_frame)+" frames"

        frame = cv2.bitwise_and(frame, frame, mask=msk)

        haar_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
        cars = car_cascade.detectMultiScale(haar_frame, 1.2, 1)
        # draw contours and hull points
        for i in range(len(contours)):
            color_contours = (0, 255, 0)  # green - color for contours
            color = (255, 0, 0)  # blue - color for convex hull
            cv2.drawContours(frame, contours, i, color, 1, 8)
            x, y, w, h = cv2.boundingRect(contours[i])
            if w > BB_MIN_WIDTH and h > BB_MIN_HEIGHT:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                count_in_blob = get_vehicle_count_in_blob(cars, contours[i])
                v_count = 1
                if count_in_blob > 1:
                    v_count = count_in_blob
                local_bbs.append([x, y, w, h, -1, [], -1, v_count])
        ############################################################# tracking
        next_id, updated_local_bbs = update(global_bbs, local_bbs, next_id)
        for bb in updated_local_bbs:
            text = str(bb[4])+" c:"+str(bb[7])
            cv2.putText(frame, text, (bb[0], bb[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            total_vehicles = total_vehicles + bb[7]
        cv2.putText(frame, str(total_vehicles), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        global_bbs.append(updated_local_bbs)
        frame_count = frame_count + 1

        if REF_SPEED_MODE:
            ref_speed = speed_by_ref_points(upper_row, lower_row, updated_local_bbs, upper_dic, lower_dic, frame_count, frame_rate, real_dis, frame_thresh)
            if ref_speed != 0:
                avg_speed = ref_speed
            cv2.circle(frame, (10, upper_row), 5, (255, 0, 0), -1)
            cv2.circle(frame, (10, lower_row), 5, (255, 0, 0), -1)
        else:
            if (frame_count % frame_interval) == 0:
                avg_speed = int(count_and_speed(global_bbs, frame_interval, wght, bis, real_car_length, frame_rate))
        cv2.putText(frame, str(avg_speed) + "kmph", (35, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #############################################################

        ped_green_light = get_decision(sim, total_vehicles, ped_count_in_roi, avg_speed, wait_frame_count, requirement_threshold)

        display_out = np.zeros((300, 350, 3), dtype="uint8")
        cv2.putText(display_out, "frame count: "+str(frame_count), (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(display_out, "Average speed : " + str(avg_speed) + "kmph", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(display_out, "Vehicle count : " + str(total_vehicles) , (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        total_vehicles = 0
        cv2.putText(display_out, "Wait time : " + str(wait_frame_count), (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(display_out, "Pedestrian count : " + str(ped_count_in_roi), (15, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(display_out, "Pedestrian: " + str(ped_green_light), (15, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
        end = timer()
        print(int(1/(end-start)))  # This FPS represent processing power of algo. this isn't video FPS
        cv2.imshow('video', frame)
        cv2.imshow('img_output', img_output)
        cv2.imshow('img_bgmodel', img_bgmodel)
        cv2.imshow('Output Display', display_out)

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
