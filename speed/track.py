import numpy as np
from speed.bb_distance import get_distance

def update(global_list, local_list, next_id):
    if len(global_list) == 0:
        for bb in local_list:
            bb[4] = next_id
            next_id = next_id + 1
        return next_id
    previous_local_list = global_list[-1]
    loc_len = len(local_list)
    pre_len = len(previous_local_list)
    matrix = np.full((pre_len, loc_len), -1)
    for p_idx, pre in enumerate(previous_local_list):
        P_blob_id, p_merge, p_split, p_v_count = pre[4:]
        for c_idx, curr in enumerate(local_list):
            c_blob_id, c_merge, c_split, c_v_count = curr[4:]
            matrix[p_idx][c_idx] = get_distance(pre[:4], curr[:4])
            # print("ok")
    return 0
