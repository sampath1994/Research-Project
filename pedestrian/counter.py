import cv2
import numpy as np
import pickle
from pathlib import Path

def is_in_roi(ped_x, ped_y, roi_cont):
    # check given pedestrian coordinate in the ROI
    val = cv2.pointPolygonTest(roi_cont, (ped_x, ped_y), False)
    if val == 1 or val == 0:  # if pedestrian centroid in the given roi
        return True
    else:
        return False

def get_roi_contour(width, height):
    with open(str(Path.cwd().parent / 'pedestrian' / 'screen-mark' / 'roi_markings.pkl'), 'rb') as inp:
        coords = pickle.load(inp)
        print(coords)
        img = np.zeros((width, height, 3), dtype="uint8")
        poly = np.array([coords], np.int32)
        cv2.polylines(img, [poly], True, (0, 255, 0), thickness=3)
        gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rt, msk = cv2.threshold(gry, 30, 255, cv2.THRESH_BINARY)
        cv2.imshow('sd', msk)
        im2, contours, hierarchy = cv2.findContours(msk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

def get_count_change(pre_objs, current_objs):
    count_chng = 0
    if len(pre_objs)!=0 and len(current_objs)!=0:
        for p_ob in pre_objs:
            for c_obj in current_objs:
                if p_ob[0] == c_obj[0]:
                    if p_ob[1] == 'o' and c_obj[1] == 'i':  # came inside
                        count_chng = count_chng + 1
                    if p_ob[1] == 'i' and c_obj[1] == 'o':  # went outside
                        count_chng = count_chng - 1
    return count_chng  # output can be positive or negative integer

def is_empty_roi(objs1, objs2):
    count = 0
    for ob in objs1:
        if ob[1] == 'i':
            count = count + 1
    for ob in objs2:
        if ob[1] == 'i':
            count = count + 1
    if count == 0:
        return True
    else:
        return False
