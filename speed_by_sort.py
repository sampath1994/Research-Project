import pandas as pd
import numpy as np
import cv2

def metadata():
    df = pd.read_csv("weights.csv", delimiter=',', header=None)
    w = float(df[0].values)
    b = float(df[1].values)
    print(w, b)
    return w, b

def measure_real_length(start_row, end_row, w, b, real_car_length):
    distance = (real_car_length / w) * (np.log(w * end_row + b) - np.log(w * start_row + b))
    return distance

def measure_speed(detections, frame, frame_num):
    # frame_num = len(detections[0])
    w, b = metadata()
    frame_rate = 30
    car_real_length = 4    # real car length in meters
    inaccurate_height = 160  # top pixel height abandoned from frame as centroid displacements are inaccurate
    final_speeds = []  # speeds taken through cluster of frames
    for det in detections:
        _, sy1, _, sy2, car_id = det[0]
        start_row = ((sy2 - sy1)/2) + sy1
        x1, ey1, _, ey2, _ = det[frame_num-1]
        end_row = ((ey2 - ey1) / 2) + ey1
        real_dis = measure_real_length(start_row, end_row, w, b, car_real_length)
        time = (1/frame_rate) * (frame_num-1)
        speed = real_dis / time
        # speed = mean_row_displacement(det, w, b, frame_num, frame_rate, car_real_length)  # mean method
        kmh_speed = round(speed*3.6)
        text = str(kmh_speed)
        if end_row > inaccurate_height:
            cv2.putText(frame, text, (int(x1), int(ey1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            final_speeds.append([car_id, kmh_speed, det[frame_num-1]])
        track_tail(det, frame)
    return final_speeds

def track_tail(det, frame):  # draw tail of BB centroid
    for fr in det:
       x1, y1, x2, y2, _ = fr
       cx = int(round(x1 + (x2 - x1)/2))
       cy = int(round(y1 + (y2 - y1) / 2))
       cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

def mean_row_displacement(det, w, b, frame_num, frame_rate, car_real_length):
    dist = 0
    for index, fr in enumerate(det):
        if index != 0:
            _, sy1, _, sy2, _ = fr
            end_row = ((sy2 - sy1) / 2) + sy1
            x1, ey1, _, ey2, _ = det[index-1]
            start_row = ((ey2 - ey1) / 2) + ey1
            if end_row < start_row:
                print("gotttttttttttttttttttt")
            dist = dist + abs(measure_real_length(start_row, end_row, w, b, car_real_length))
    speed = (dist / (frame_num-1)) / (1/frame_rate)
    return speed
