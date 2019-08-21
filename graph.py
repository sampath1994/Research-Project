import cv2
import numpy as np
def process_graph(cleared_final_detections , frame):
    for detection_set in cleared_final_detections:
        compute_ratio(detection_set, frame)

def find_center(detection):
    x1, y1, x2, y2, obj_id = detection
    w = x2 - x1
    h = y2 - y1
    center_x = x1 + w/2
    center_y = y1 + h/2
    return [center_x,center_y]

def compute_ratio(detection_set,frame):
    centroid_list = []
    for det in detection_set:
        centroid_list.append(find_center(det))
    np_centroid_list = np.array(centroid_list)
    [vx, vy, x, y] = cv2.fitLine(np_centroid_list, cv2.DIST_L2, 0, 0.01, 0.01)
    lefty = int((-x * vy / vx) + y)
    righty = int(((frame.shape[1] - x) * vy / vx) + y)
    cv2.line(frame, (frame.shape[1] - 1, righty), (0, lefty), 255, 2)