import numpy as np
from speed.bb_distance import get_distance
import cv2

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


def get_vehicle_count_in_blob(cars, contour):
    count = 0
    for (x, y, w, h) in cars:
        cx = int(x + (w/2))
        cy = int(y + (h/2))
        if cv2.pointPolygonTest(contour, (cx, cy), False) == 1:
            count = count + 1
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