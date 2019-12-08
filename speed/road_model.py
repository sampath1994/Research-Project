import numpy as np
import cv2
import pybgs as bgs
from pathlib import Path

def draw_RS_map(md ,w ,h):
    mx = 0
    for p in range(w - 1):
        for r in range(h - 1):
            if md[r][p] > mx:
                mx = md[r][p]
    print(mx)
    black = np.zeros((h, w, 3), np.uint8)
    for p in range(w - 1):
        for r in range(h - 1):
            black[r][p] = int((md[r][p] / mx) * 255)
    cv2.imshow('Road_modle', black)
    cv2.imwrite('road_model.jpg', black)
    cv2.waitKey()

algorithm = bgs.MultiLayer()
#video_file = "C:/Users/promod/Desktop/researchPapers/yolo-object-detection/videos/video03.avi"
video_file = str(Path.cwd().parent / 'videos' / 'video03.avi')

capture = cv2.VideoCapture(video_file)
while not capture.isOpened():
    capture = cv2.VideoCapture(video_file)
    cv2.waitKey(1000)
    print("Wait for the header")

#pos_frame = capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
#pos_frame = capture.get(cv2.CV_CAP_PROP_POS_FRAMES)
pos_frame = capture.get(1)
width = int(capture.get(3))
height = int(capture.get(4))

model = []
for row in range(height):
    model.append({x: 0 for x in range(width)})

while True:
    flag, frame = capture.read()

    if flag:
        # cv2.imshow('video', frame)
        #pos_frame = capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        #pos_frame = capture.get(cv2.CV_CAP_PROP_POS_FRAMES)
        pos_frame = capture.get(1)
        #print str(pos_frame)+" frames"

        img_output = algorithm.apply(frame)
        img_bgmodel = algorithm.getBackgroundModel()

        img_output = cv2.dilate(img_output, None, iterations=3)
        img_output = cv2.erode(img_output, None, iterations=1)
        ############################################################# convex hull drawing
        im2, contours, hierarchy = cv2.findContours(img_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        hull = []
        for i in range(len(contours)):
            # creating convex hull object for each contour
            hull.append(cv2.convexHull(contours[i], False))

        # draw contours and hull points
        for i in range(len(contours)):
            color_contours = (0, 255, 0)  # green - color for contours
            color = (255, 0, 0)  # blue - color for convex hull
            cv2.drawContours(frame, hull, i, color, 1, 8)
        #############################################################

        for i in range(width-1):
            for j in range(height-1):
                k = img_output[j, i]
                if k == 255:
                    model[j][i] = model[j][i] + 1



        cv2.imshow('video', frame)
        cv2.imshow('img_output', img_output)
        cv2.imshow('img_bgmodel', img_bgmodel)

    else:
        #capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
        #capture.set(cv2.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
        #capture.set(1, pos_frame-1)
        #print "Frame is not ready"
        cv2.waitKey(1000)
        break

    if 0xFF & cv2.waitKey(10) == 27:
        draw_RS_map(model, width, height)
        # cv2.imwrite('background.jpg', img_bgmodel)
        break

    #if capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
    #if capture.get(cv2.CV_CAP_PROP_POS_FRAMES) == capture.get(cv2.CV_CAP_PROP_FRAME_COUNT):
    #if capture.get(1) == capture.get(cv2.CV_CAP_PROP_FRAME_COUNT):
    #break
draw_RS_map(model, width, height)
cv2.destroyAllWindows()


