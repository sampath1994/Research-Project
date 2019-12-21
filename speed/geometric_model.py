import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.signal import find_peaks

def score_graph_of_row(img, row, boundry_thr):
    height, width = img.shape
    score = []
    x = []
    width = width - 1
    for i in range(width):
        score.append(img[row][i])
        x.append(i)
    left, right = road_boundary_v2(score, boundry_thr)
    score = invert_graph(score)
    peaks, _ = find_peaks(score, prominence=40)  # change prominence to extract inverted valleys (lane divisions)
    local_max = list(peaks)
    ####################################
    # local_max.append(left)
    # local_max.append(right)
    # plt.plot(x, score, '-gD', markevery=local_max)
    # plt.show()
    ####################################
    return local_max, left, right

def invert_graph(scores):
    max_score = max(scores)
    inverted = max_score - scores
    return inverted

def road_boundary(scores, thresh):  # ----->  <-----  outside to inside boundary detect
    left = 0
    right = 0
    for idx, lft in enumerate(scores):
        if lft > thresh:
            left = idx
            break
    for idx, rht in reversed(list(enumerate(scores))):
        if rht > thresh:
            right = idx
            break
    return left, right

def road_boundary_v2(scores, thresh):
    left = 0
    right = 0
    peaks, _ = find_peaks(scores, prominence=40)  # change prominence to extract peaks (vehicle paths)
    peak_list = list(peaks)
    if len(peak_list) != 0:
        lefty_peak = peak_list[0]
        righty_peak = peak_list[-1]
        lefty_peak = lefty_peak + 1
        for idx, i in reversed(list(enumerate(scores[:lefty_peak]))):
            if i < thresh:
                left = idx
                break
        for idx, i in list(enumerate(scores[righty_peak:])):
            if i < thresh:
                right = righty_peak + idx
                break
    return left, right

# Load an color image in grayscale
img = cv2.imread('road_model.jpg', 0)
ROAD_BOUNDRY_THRESH = 10
new_img = cv2.imread('background.jpg', cv2.IMREAD_COLOR)
height, width = img.shape
left_boundary_img = np.zeros(shape=[height, width, 3], dtype=np.uint8)
right_boundary_img = np.zeros(shape=[height, width, 3], dtype=np.uint8)

for row in range(height):
    vall, leftB, rightB = score_graph_of_row(img, row, ROAD_BOUNDRY_THRESH)  # 220
    for pnt in vall:
        cv2.circle(new_img, (pnt, row), 1, (0, 0, 255), -1)
    cv2.circle(new_img, (leftB, row), 1, (0, 255, 0), -1)
    cv2.circle(new_img, (rightB, row), 1, (0, 255, 0), -1)
    cv2.circle(left_boundary_img, (leftB, row), 1, (0, 255, 0), -1)
    cv2.circle(right_boundary_img, (rightB, row), 1, (0, 255, 0), -1)
ret, th = cv2.threshold(img,20,255,cv2.THRESH_BINARY)
########################################
init_mask = np.zeros(shape=[height, width, 1], dtype=np.uint8)
left_boundary_img = cv2.cvtColor(left_boundary_img, cv2.COLOR_BGR2GRAY)
right_boundary_img = cv2.cvtColor(right_boundary_img, cv2.COLOR_BGR2GRAY)
rt, left_th = cv2.threshold(left_boundary_img,10,255,cv2.THRESH_BINARY)
rt2, right_th = cv2.threshold(right_boundary_img,10,255,cv2.THRESH_BINARY)

for j in range(height - 1):
    flg = False
    for i in reversed(range(width - 1)):
        k = left_boundary_img[j, i]
        if k > 100:
            flg = True
        if flg:
            init_mask[j, i] = 255

for j in range(height - 1):
    flg = False
    for i in range(width - 1):
        k = right_boundary_img[j, i]
        if k > 100:
            flg = True
        if flg:
            init_mask[j, i] = 255

########################################
init_mask = cv2.bitwise_not(init_mask)
cv2.imwrite('mask.jpg', init_mask)
cv2.imshow('Thresh', th)
cv2.imshow('Model', new_img)
cv2.imshow('Left', left_th)
cv2.imshow('Right', right_th)
cv2.imshow('Mask', init_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()