import numpy as np
from speed.bb_distance import get_distance

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
            for i in zero_idxs:
                curr[5].append(previous_local_list[i][4])  # previous track ids of merge put into current bb merge list
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
                local_list[i][6] = pre[4]
        if zero_count == 0:
            print("track lost", pre[4])
    return next_id, local_list
