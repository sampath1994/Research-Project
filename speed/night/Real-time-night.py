import cv2
import numpy as np
from pathlib import Path
from timeit import default_timer as timer
from speed.night.rules import is_grouped, get_group_bb, is_vehicle
from sort import *

video_file = str(Path.cwd().parent.parent / 'videos' / 'CCTV night video.mp4')
camera = cv2.VideoCapture(video_file)

BB_MIN_HEIGHT = 2
BB_MIN_WIDTH = 2
mot_tracker = Sort()

while True:
    start = timer()
    (grabbed,frame) = camera.read()
    grayvideo = cv2.cvtColor(frame,  cv2.COLOR_BGR2YCR_CB)

    y, cr, cb = cv2.split(grayvideo)
    blur = cv2.GaussianBlur(y,(5,5),0)
    ret2, th2 = cv2.threshold(blur, 240, 255, cv2.THRESH_BINARY)
    im2, contours, hierarchy = cv2.findContours(th2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bbs = []
    for i in range(len(contours)):
        color_contours = (0, 255, 0)  # green - color for contours
        color = (255, 0, 0)  # blue - color for convex hull
        cv2.drawContours(frame, contours, i, color, 1, 8)
        x, y, w, h = cv2.boundingRect(contours[i])
        if w > BB_MIN_WIDTH and h > BB_MIN_HEIGHT:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            bbs.append((i, x, y, w, h))
    mot_before_list = []
    bb_len = len(bbs) - 1
    for idx, bb in enumerate(bbs):
        if idx != bb_len:
            for itm in bbs[idx + 1:]:
                if is_grouped(bb[1:], itm[1:]):
                    tlx, tly, brx, bry = get_group_bb(bb[1:], itm[1:])
                    cv2.rectangle(frame, (tlx, tly), (brx, bry), (0, 0, 255), 2)
                    if is_vehicle(tlx, tly, brx, bry, contours, bb[0], itm[0]):
                        cv2.rectangle(frame, (tlx, tly), (tlx+5, tly+5), (255, 0, 0), 2)
                        mot_before_list.append([tlx, tly, brx, bry, 0.8])
    mot_before_np = np.array(mot_before_list)
    track_bbs_ids = mot_tracker.update(mot_before_np)
    mot_x1, mot_y1, mot_x2, mot_y2, obj_id = [0,0,0,0,0]
    for i in track_bbs_ids:
        mot_x1, mot_y1, mot_x2, mot_y2, obj_id = i
        x1_i = int(mot_x1)
        y1_i = int(mot_y1)
        x2_i = int(mot_x2)
        y2_i = int(mot_y2)
        cv2.rectangle(frame, (x1_i, y1_i), (x2_i, y2_i), (255,0,0), 2)
        text = str(obj_id)
        cv2.putText(frame, text, (x1_i, y1_i - 7),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
    cv2.imshow("video", frame)
    cv2.imshow("converted", th2)
    end = timer()
    print(int(1/(end - start)))
    if cv2.waitKey(10) == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()

