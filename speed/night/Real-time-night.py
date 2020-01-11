import cv2
import numpy as np
from pathlib import Path
from timeit import default_timer as timer
from speed.night.rules import is_grouped, get_group_bb

video_file = str(Path.cwd().parent.parent / 'videos' / 'CCTV night video.mp4')
camera = cv2.VideoCapture(video_file)

BB_MIN_HEIGHT = 2
BB_MIN_WIDTH = 2

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
    bb_len = len(bbs) - 1
    for idx, bb in enumerate(bbs):
        if idx != bb_len:
            for itm in bbs[idx + 1:]:
                if is_grouped(bb[1:], itm[1:]):
                    # lx = min(bb[1], itm[1])
                    # ly = min(bb[2], itm[2])
                    # rx = max(bb[1], itm[1])
                    # ry = max(bb[2], itm[2])
                    tlx, tly, brx, bry = get_group_bb(bb[1:], itm[1:])
                    cv2.rectangle(frame, (tlx, tly), (brx, bry), (0, 0, 255), 2)

    cv2.imshow("video", frame)
    cv2.imshow("converted", th2)
    end = timer()
    print(int(1/(end - start)))
    if cv2.waitKey(10) == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()

