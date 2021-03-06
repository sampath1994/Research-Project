import numpy as np
import cv2
import pybgs as bgs
from pathlib import Path
import pandas as pd
from timeit import default_timer as timer
from speed.track import update, get_vehicle_count_in_blob, count_and_speed, speed_by_ref_points, load_speed_coord, update_cascade_bb, is_full_congestion
from fuzzy_decision.Decision import init_fuzzy_system, get_decision, get_graph
import argparse

ARGS = True
ap = argparse.ArgumentParser()
if ARGS:
    ap.add_argument("-i1", "--input1", required=True)
    ap.add_argument("-i2", "--input2", required=True)
    ap.add_argument("-i3", "--input3", required=True)
    ap.add_argument("-i4", "--input4", required=True)
    ap.add_argument("-i5", "--input5", required=True)
    ap.add_argument("-i6", "--input6", required=True)
    ap.add_argument("-i7", "--input7", required=True)
    ap.add_argument("-i8", "--input8", required=True)
    ap.add_argument("-i9", "--input9", required=True)
    args = vars(ap.parse_args())
algorithm = bgs.MultiLayer()
video_file = str(Path.cwd().parent / 'videos' / 'video03.avi')
if ARGS:
    video_file = args["input1"]
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
frame_rate = capture.get(cv2.CAP_PROP_FPS)
df = pd.read_csv(speed_weight_file, delimiter=',', header=None)
wght = float(df[0].values)
bis = float(df[1].values)
real_car_length = 4  # put mean car length in meters
upper_dic = {}
lower_dic = {}
REF_SPEED_MODE = False
BOTH_CHANNEL = True
real_dis = 5  # 15 for simulator videos  # real distance in Meters, between marked reference points
frame_thresh = 250  # clean dictionaries older than frame threshold
cascade_bb_counts = []  # haar cascade detections for few frames
start_decision_flg = False  # flag true for defined time to take decision
decision_count = 0
decision_ok_count = 0
vehicle_frms_per_round = 6
ped_frms_per_round = 1
Mask = True
if ARGS:
    if args["input3"] == "yes":
        Mask = True
    else:
        Mask = False
    vehicle_frms_per_round = int(args["input4"])
    ped_frms_per_round = int(args["input5"])
    if args["input6"] == "yes":
        REF_SPEED_MODE = True
    else:
        REF_SPEED_MODE = False
    if args["input7"] == "yes":
        BOTH_CHANNEL = True
    else:
        BOTH_CHANNEL = False
    real_dis = int(args["input9"])
if REF_SPEED_MODE:
    upper_row, lower_row = load_speed_coord(str(Path.cwd() / 'screen-mark' / 'speed_markings.pkl'))
    if ARGS:
        if args["input8"] == "1":
            upper_row, lower_row = load_speed_coord(str(Path.cwd() / 'screen-mark' / 'speed_markings.pkl'))
        elif args["input8"] == "2":
            upper_row, lower_row = load_speed_coord(str(Path.cwd() / 'screen-mark' / 'speed_markings-2.pkl'))
###########################################################################
from sort import *
from pedestrian.counter import get_roi_contour
from pedestrian.pedestrian_Detection import ped

ped_file = str(Path.cwd().parent / 'videos' / 'pedestrians.avi')
if ARGS:
    ped_file = args["input2"]
camera = cv2.VideoCapture(ped_file)
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
standing_thresh = 2
wait_time = 0
###########################################################################
arr_v = []
arr_p = []
arr_s = []
arr_w = []
arr_decision = []
Tot_count = []
###########################################################################
sim = init_fuzzy_system()
requirement_threshold = 4

while True:
    flag, frame = capture.read()
    ##############################
    if BOTH_CHANNEL:
        if frame_count % vehicle_frms_per_round == 0:  # MOD value = Higher FPS / Lower FPS
            for z in range(ped_frms_per_round):
                (grabbed, framez) = camera.read()
                if grabbed:
                    ped_count_in_roi, frm_count, wait_frame_count = ped(framez, ped_cascade, current_objs, cont, frm_count, ped_count_in_roi, wait_frame_count, mot_tracker, standing_thresh)
                    wait_time = int(wait_frame_count*0.1)
    ##############################
    local_bbs = []
    if flag:
        start = timer()
        # cv2.imshow('video', frame)
        #pos_frame = capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        #pos_frame = capture.get(cv2.CV_CAP_PROP_POS_FRAMES)
        pos_frame = capture.get(1)
        #print str(pos_frame)+" frames"

        if Mask:
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

        ped_green_light = get_decision(sim, total_vehicles, ped_count_in_roi, avg_speed, wait_time, requirement_threshold)

        display_out = np.zeros((300, 350, 3), dtype="uint8")
        cv2.putText(display_out, "frame count: "+str(frame_count), (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(display_out, "Average speed : " + str(avg_speed) + "kmph", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(display_out, "Vehicle count : " + str(total_vehicles) , (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        #######################################
        arr_v.append(total_vehicles)
        update_cascade_bb(cascade_bb_counts, len(cars))
        if total_vehicles == 0:
            if is_full_congestion(cascade_bb_counts):
                print("!!High congestion detected!!")
            else:
                print("Empty road")
        #######################################
        total_vehicles = 0
        cv2.putText(display_out, "Wait time : " + str(wait_time), (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(display_out, "Pedestrian count : " + str(ped_count_in_roi), (15, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(display_out, "Pedestrian: " + str(ped_green_light), (15, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
        ########################################
        arr_p.append(ped_count_in_roi)
        arr_s.append(avg_speed)
        arr_w.append(wait_time)
        if ped_green_light:
            arr_decision.append(5)
            start_decision_flg = True
        else:
            arr_decision.append(0)
        if start_decision_flg:
            decision_count = decision_count + 1
            if ped_green_light:
                decision_ok_count = decision_ok_count + 1
        if decision_count > (30):  # frame_rate/4
            percentage = (decision_ok_count / decision_count)*100
            if percentage > 70:
                print("!Green light for pedestrians!")
                break
            decision_count = 0
            decision_ok_count = 0
            start_decision_flg = False
        ########################################
        end = timer()
        print("FPS: ", int(1/(end-start)))  # This FPS represent processing power of algo. this isn't video FPS
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

    #if frame_count % 60 == 0:
        #print("take values!")

    k = cv2.waitKey(10)
    if k == ord('q'):
        break
    elif k == ord('s'):
        cv2.imwrite('day_still.jpg', frame)

    #if capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
    #if capture.get(cv2.CV_CAP_PROP_POS_FRAMES) == capture.get(cv2.CV_CAP_PROP_FRAME_COUNT):
    #if capture.get(1) == capture.get(cv2.CV_CAP_PROP_FRAME_COUNT):
    #break
get_graph(arr_v, arr_p, arr_s, arr_w, arr_decision)
cv2.destroyAllWindows()
