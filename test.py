import cv2
import numpy as np
FRAMES = 3
# Load image, convert to grayscale, threshold and find contours
img = cv2.imread('lailP.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
_, contours, hier = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
# cnt = contours[0]
cnt = np.arange(FRAMES*2).reshape(FRAMES, 2)
cnt[0][0] = 5
cnt[0][1] = 5
cnt[1][0] = 50
cnt[1][1] = 50
cnt[2][0] = 123
cnt[2][1] = 42
# then apply fitline() function
[vx,vy,x,y] = cv2.fitLine(cnt,cv2.DIST_L2,0,0.01,0.01)
# Now find two extreme points on the line to draw line
lefty = int((-x*vy/vx) + y)
righty = int(((gray.shape[1]-x)*vy/vx)+y)

# Finally draw the line
cv2.line(img,(gray.shape[1]-1,righty),(0,lefty),255,2)
cv2.circle(img, (5, 5), 5, (0, 0, 255), -1)
cv2.circle(img, (50, 50), 5, (0, 0, 255), -1)
cv2.circle(img, (123, 42), 5, (0, 0, 255), -1)
cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()