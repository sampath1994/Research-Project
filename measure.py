from graph import process_graph
from speed_by_sort import measure_speed
import cv2

def calc_vehicle_len(detection_buff, frm, car_len, is_train):
    frames = len(detection_buff)
    frame_1_detec = detection_buff[0]
    final_detections = []
    cleared_final_detections = []
    for frame in range(1, frames):
        for k in frame_1_detec:
            x1, y1, x2, y2, obj_id = k
            next_frame_detec = detection_buff[frame]
            for r in next_frame_detec:
                a1, b1, a2, b2, obj_id2 = r
                if obj_id == obj_id2:
                    if len(final_detections) != 0:
                        no_detection = True
                        for val in final_detections:
                            if val[0][4] == obj_id:
                                val.append(r)
                                no_detection = False

                        if no_detection:
                            final_detections.append([k, r])
                    else:
                        final_detections.append([k, r])
    print(final_detections)
    for det in final_detections:  # remove tuples with frames less than 'frames' value
        if len(det) == frames:
            cleared_final_detections.append(det)
    print(cleared_final_detections)
    if is_train:
        return process_graph(cleared_final_detections, frm, car_len)
    else:
        return measure_speed(cleared_final_detections, frm, frames)


def count_vehicles(class_id_list, frame):
    vehicle_ids = [1,2,3,5,7]
    total_vehicle_count = 0
    for vehicle in class_id_list:
        if vehicle in vehicle_ids:
            total_vehicle_count = total_vehicle_count + 1
    text = "Vehicle count : " + str(total_vehicle_count)
    cv2.putText(frame, text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)