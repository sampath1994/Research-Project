import cv2
import numpy as np
from pathlib import Path
from timeit import default_timer as timer

video_file = str(Path.cwd().parent.parent / 'videos' / 'CCTV night video.mp4')
camera = cv2.VideoCapture(video_file)

while True:
    start = timer()
    (grabbed,frame) = camera.read()
    grayvideo = cv2.cvtColor(frame,  cv2.COLOR_BGR2YCR_CB)

    y, cr, cb = cv2.split(grayvideo)
    blur = cv2.GaussianBlur(y,(5,5),0)
    ret2, th2 = cv2.threshold(blur, 240, 255, cv2.THRESH_BINARY)
    # th3 = cv2.adaptiveThreshold(y, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 251, 5)

    cv2.imshow("video", frame)
    cv2.imshow("converted", th2)
    end = timer()
    print(int(1/(end - start)))
    if cv2.waitKey(10) == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()

