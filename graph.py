import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
import csv
def process_graph(cleared_final_detections , frame, car_len):
    frameset_ratios = []
    for detection_set in cleared_final_detections:
        frame_row, ratio = compute_ratio(detection_set, frame, car_len)
        if ratio > 0 and frame_row > 360:
            frameset_ratios.append([frame_row, ratio])
    print(frameset_ratios)
    return frameset_ratios

def find_center(detection):
    x1, y1, x2, y2, obj_id = detection
    w = x2 - x1
    h = y2 - y1
    center_x = x1 + w/2
    center_y = y1 + h/2
    return [center_x,center_y]

def compute_ratio(detection_set,frame, car_len):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    centroid_list = []
    for det in detection_set:
        centroid_list.append(find_center(det))
    np_centroid_list = np.array(centroid_list)
    [vx, vy, x, y] = cv2.fitLine(np_centroid_list, cv2.DIST_L2, 0, 0.01, 0.01)
    lefty = int((-x * vy / vx) + y)
    righty = int(((frame.shape[1] - x) * vy / vx) + y)
    cv2.line(frame, (frame.shape[1] - 1, righty), (0, lefty), 255, 2)
    pixel_row, pixel_len = median_intersection_length(detection_set, vx, vy, lefty)
    if pixel_len>0:
        # ratio = car_len/pixel_len    # now giving the pixel length
        ratio = pixel_len
        return pixel_row, ratio
    else:
        return pixel_row, -1

def median_intersection_length(detection_set,vx,vy,lefty):
    length = len(detection_set)
    middle = int(length/2) + 1
    m = vy / vx
    x1, y1, x2, y2, obj_id = detection_set[middle-1]  # from here onwards working on one bounding box
    upper_x = (y1-lefty) / m
    upper = [upper_x, y1]
    lower_x = (y2-lefty) / m
    lower = [lower_x, y2]
    median_frm_center = find_center(detection_set[middle-1])
    if x1<upper_x and upper_x<x2 and x1<lower_x and lower_x<x2:
        pixel_dist_car = math.sqrt((upper_x - lower_x) ** 2 + (y2 - y1) ** 2)
        return median_frm_center[1], pixel_dist_car
    else:
        return median_frm_center[1], -1

def draw_ratio_graph(ratio_list):
    row_values = []
    ratio_values = []
    for item in ratio_list:
        row, ratio = item
        row_values.append(row)
        ratio_values.append(ratio)
    plt.plot(row_values,ratio_values, 'ro')
    plt.ylabel('Pixel length')
    plt.xlabel('Row number of a frame')
    plt.show()
    write_csv(row_values, ratio_values)

def write_csv(rows,ratios):
    with open('ratio_data.csv', 'w', newline='') as myfile:
        zipped_rows = zip(rows, ratios)
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for one_row in zipped_rows:
            wr.writerow(one_row)
        print("Done CSV write")