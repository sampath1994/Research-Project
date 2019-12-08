import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.signal import find_peaks

def score_graph_of_row(img, row):
    height, width = img.shape
    score = []
    x =[]
    width = width - 1
    for i in range(width):
        score.append(img[row][i])
        x.append(i)
    # local_max = list(argrelextrema(np.array(score), np.greater_equal, order=1))
    score = invert_graph(score)
    peaks, _ = find_peaks(score, prominence=40)
    local_max = list(peaks)
    # plt.plot(x, score, '-gD', markevery=local_max)
    # plt.show()
    return local_max

def invert_graph(scores):
    max_score = max(scores)
    inverted = max_score - scores
    return inverted


# Load an color image in grayscale
img = cv2.imread('road_model.jpg', 0)
new_img = cv2.imread('background.jpg', cv2.IMREAD_COLOR)
height, width = img.shape
for row in range(height):
    vall = score_graph_of_row(img, row)  # 220
    for pnt in vall:
        cv2.circle(new_img, (pnt, row), 1, (0, 0, 255), -1)
ret, th = cv2.threshold(img,40,255,cv2.THRESH_BINARY)
cv2.imshow('Thresh', th)
cv2.imshow('Model', new_img)
cv2.waitKey(0)
cv2.destroyAllWindows()