import cv2
from timeit import default_timer as timer
from sort import *
from pedestrian.counter import get_roi_contour, is_in_roi, get_count_change, is_empty_roi

    # camera = cv2.VideoCapture("pedestrians.avi")
    # camera.open("pedestrians.avi")
    # ped_cascade = cv2.CascadeClassifier('cascade3.xml')
    # frame_count = 0
    # # create instance of SORT
    # mot_tracker = Sort()
    # cont = get_roi_contour(int(camera.get(4)), int(camera.get(3)))
    # pre_objs = []
    # current_objs = []
    # ped_count_in_roi = 0
    # while True:

def ped(frame, ped_cascade, current_objs, cont, frame_count, ped_count_in_roi, mot_tracker):
    start = timer()
    grayvideo = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cars = ped_cascade.detectMultiScale(grayvideo, 1.1, minNeighbors=4)  # 1.1 #2

    mot_before_list = []
    for (x, y, w, h) in cars:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        mot_before_list.append([x, y, (x+w), (y+h), 0.8])
    mot_before_np = np.array(mot_before_list)
    track_bbs_ids = mot_tracker.update(mot_before_np)
    mot_x1, mot_y1, mot_x2, mot_y2, obj_id = [0, 0, 0, 0, 0]
    trk_with_wid_hgt = []
    pre_objs = current_objs.copy()  # keep copy in buffer
    current_objs[:] = []  # make current list empty
    for i in track_bbs_ids:
        mot_x1, mot_y1, mot_x2, mot_y2, obj_id = i
        x1_i = int(mot_x1)
        y1_i = int(mot_y1)
        x2_i = int(mot_x2)
        y2_i = int(mot_y2)
        cv2.rectangle(frame, (x1_i, y1_i), (x2_i, y2_i), (255, 0, 0), 2)
        text = str(obj_id)
        print(text)
        cv2.putText(frame, text, (x1_i, y1_i - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        wid = x2_i - x1_i
        higt = y2_i - y1_i
        trk_with_wid_hgt.append([x1_i, y1_i, wid, higt, obj_id])
        cen_x = x1_i + wid / 2
        cen_y = y1_i + higt / 2
        if is_in_roi(cen_x, cen_y, cont[0]):
            current_objs.append((obj_id, 'i'))
        else:
            current_objs.append((obj_id, 'o'))
    frame_count_return = frame_count + 1
    cv2.drawContours(frame, cont, 0, (255, 0, 0), 2, 8)
    chng = get_count_change(pre_objs, current_objs)
    buff = ped_count_in_roi + chng
    if buff < 0:  # This is resetting procedure
        ped_count_in_roi_return = 0
    else:
        ped_count_in_roi_return = buff
    if is_empty_roi(pre_objs, current_objs):  # This is also resetting procedure
        ped_count_in_roi_return = 0
    cv2.putText(frame, str(ped_count_in_roi_return), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow("vid", frame)
    end = timer()
    print(int(1 / (end - start)))

    return ped_count_in_roi_return, frame_count_return
    # k = cv2.waitKey(10)
    # if k == ord('q'):
    #     break
    # elif k == ord('s'):
    #     cv2.imwrite('pedestrian_still.jpg', frame)

# camera.release()
# cv2.destroyAllWindows()
