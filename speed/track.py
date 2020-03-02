import numpy as np
from speed.bb_distance import get_distance
import cv2
from pathlib import Path
import pickle

def update(global_list, local_list, next_id):
    if len(global_list) == 0:  # if there is no previous bb list
        for bb in local_list:  # assign new track ids
            bb[4] = next_id
            next_id = next_id + 1
        return next_id, local_list
    previous_local_list = global_list[-1]
    loc_len = len(local_list)
    pre_len = len(previous_local_list)
    matrix = np.full((pre_len, loc_len), -1)  # the distance matrix
    for p_idx, pre in enumerate(previous_local_list):
        for c_idx, curr in enumerate(local_list):
            matrix[p_idx][c_idx] = get_distance(pre[:4], curr[:4])  # populating matrix

    for c_idx, curr in enumerate(local_list):  # iterate over each column of matrix
        zero_count = 0
        zero_idxs = []
        for idx, d in enumerate(matrix[:, c_idx]):
            if d == 0:  # find zeros in column
                zero_count = zero_count + 1
                zero_idxs.append(idx)
        if zero_count == 1:  # current match
            curr[4] = previous_local_list[zero_idxs[0]][4]  # previous id assign to current match
        elif zero_count > 1:  # Merge detected
            curr[4] = next_id  # give new track id after merge
            next_id = next_id + 1
            vehicle_count = 0
            for i in zero_idxs:
                curr[5].append(previous_local_list[i][4])  # previous track ids of merge put into current bb merge list
                vehicle_count = vehicle_count + previous_local_list[i][7]
            curr[7] = vehicle_count  # when merging vehicle counts of previous bbs are added
        elif zero_count == 0:  # completely new bb, give new track id
            curr[4] = next_id
            next_id = next_id + 1

    for p_idx, pre in enumerate(previous_local_list):  # iterate over each row
        zero_count = 0
        zero_idxs = []
        for idx, d in enumerate(matrix[p_idx]):
            if d == 0:  # find zeros in column
                zero_count = zero_count + 1
                zero_idxs.append(idx)
        if zero_count > 1:  # split detected
            for i in zero_idxs:
                local_list[i][6] = pre[4]  # assign split variable previous bb id
                local_list[i][4] = next_id  # new track ids after split
                next_id = next_id + 1
        if zero_count == 0:
            print("track lost", pre[4])
    return next_id, local_list


def get_vehicle_count_in_blob(cars, contour, frm=None):
    CONV_DEF = False
    count = 0
    for (x, y, w, h) in cars:
        cx = int(x + (w/2))
        cy = int(y + (h/2))
        if cv2.pointPolygonTest(contour, (cx, cy), False) == 1:
            count = count + 1
    if CONV_DEF and count < 2:
        con_hull = cv2.convexHull(contour,returnPoints = False)
        defects = cv2.convexityDefects(contour, con_hull)
        rect = cv2.minAreaRect(contour)
        wid = rect[1][0]
        if defects is not None:
            for defect in defects:
                d = defect[0][3]
                def_point = defect[0][2]
                xy = contour[def_point]
                d = d / 256.0
                if (d / (wid/2)) > 0.9:
                    count = 2
                    #  cv2.putText(frm, "D", (xy[0][0], xy[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    #  print("Con - Defect")
    return count

def count_and_speed(global_bbs, frame_interval, w, b, real_car_length, frame_rate):  # pass latest global_bb frames
    frame_int = frame_interval * -1
    latest_frames = global_bbs[frame_int:]
    initial_track_ids = []
    good_track_ids = []
    for bb in latest_frames[0]:
        initial_track_ids.append(bb[4])
    for track_id in initial_track_ids:
        count = 0
        for bb_list in latest_frames[1:]:
            flag = True
            for bb in bb_list:
                if bb[4] == track_id:
                    count = count + 1
                    flag = False
                    break
            if flag:
                break
        if count == (frame_interval - 1):
            good_track_ids.append(track_id)
    time = (frame_interval - 1) * (1 / frame_rate)
    total_speed = 0
    good_count = 0
    for id in good_track_ids:
        start_row = get_bb(latest_frames[0], id)
        end_row = get_bb(latest_frames[-1], id)
        if end_row > start_row:
            distance = measure_real_length(start_row, end_row, w, b, real_car_length)
            speed = distance / time  # meters per second speed
            km_speed = speed * 3.6  # kilometers per hour speed
            total_speed = total_speed + km_speed
            good_count = good_count + 1
    ave_speed = 0
    if good_count > 0:
        ave_speed = total_speed / good_count
    return ave_speed

def get_bb(bb_list, track_id):
    for bb in bb_list:
        if bb[4] == track_id:
            return int(bb[1] + (bb[3]/2))

def measure_real_length(start_row, end_row, w, b, real_car_length):
    distance = (real_car_length / w) * (np.log(w * end_row + b) - np.log(w * start_row + b))
    return distance

def speed_by_ref_points(upper_row, lower_row,bbs, upper_dic, lower_dic, frame_id, frame_rate, real_dis, frame_thresh):  # this should be called for each frame
    avg_speed = []
    del_list = []  # list of keys to be deleted from upper and lower dics
    for bb in bbs:  # for BBs in latest frame
        _, y1, _, h, ob_id = bb[:5]
        cy = int(y1 + h / 2)  # centroid y of BB
        if cy < upper_row:  # if centroid above upper bound
            upper_dic[ob_id] = frame_id
        if cy > lower_row:
            lower_dic[ob_id] = frame_id
    for key in upper_dic:  # compare obj_ids at upper and lower rows
        if key in lower_dic:  # if same obj_id exist in lower row...
            frame_diff = lower_dic[key] - upper_dic[key]  # then calculate speed using time
            time = frame_diff * (1 / frame_rate)
            speed = real_dis / time
            avg_speed.append(speed)
            del_list.append(key)
    for key in upper_dic:
        if (frame_id - upper_dic[key]) > frame_thresh:
            del_list.append(key)
    for key in lower_dic:
        if (frame_id - lower_dic[key]) > frame_thresh:
            del_list.append(key)
    for key in del_list:  # clean upper and lower dics
        try:
            del upper_dic[key]
        except:
            pass
        try:
            del lower_dic[key]
        except:
            pass
    if len(avg_speed) > 0:
        return int((sum(avg_speed) / len(avg_speed)) * 3.6)
    else:
        return 0

def load_speed_coord(coord_path):
    with open(coord_path, 'rb') as inp:
        coord_obj = pickle.load(inp)
        coord1 = coord_obj[0][1]
        coord2 = coord_obj[1][1]
        if coord1 < coord2:
            return coord1, coord2
        else:
            return coord2, coord1

def count_by_history(obj_que, latest_objs, history):
    ttl_vehicle_cont = 0  # total vehicle count in frame history
    que_len = len(obj_que)
    if que_len < history:  # if queue smaller fill it with latest frames
        obj_que.append(latest_objs)
        return 0
    elif que_len == history:
        obj_que.popleft()  # remove the oldest frame
        for i in latest_objs:  # for each object in latest frame..
            ob_count = 0
            for objs in obj_que:  # iterate over queue elements
                if i in objs:
                    ob_count = ob_count + 1
            if ob_count == len(obj_que):  # if same object reside in all frames of history then it's a clean object
                ttl_vehicle_cont = ttl_vehicle_cont + 1
        obj_que.append(latest_objs)  # add the latest obj frame to the queue
        return ttl_vehicle_cont

def update_cascade_bb(arry, current_count):
    ar_len = len(arry)
    if ar_len == 3:  # checking back for 3 frames of cascade detections
        for i in range(ar_len-1):
            arry[i] = arry[i+1]
        arry[ar_len-1] = current_count
    else:
        arry.append(current_count)

def is_full_congestion(cascade_bb_counts):
    buff_cnt = 0
    for bb_ct in cascade_bb_counts:
        if bb_ct > 4:  # each frame should hold at least 4 bounding boxes
            buff_cnt = buff_cnt + 1
    if buff_cnt > 3:
        return True
    else:
        return False
