import cv2
import pickle
import numpy as np
#img = np.zeros((512,512,3), np.uint8)
img = cv2.imread("C:\\Users\\promod\\Desktop\\researchPapers\\yolo-object-detection\\speed\\background.jpg")
coordinates = []
def draw_circle(event, x, y, flags, param):
    # global mouseX,mouseY
    global coordinates
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
        #mouseX,mouseY = x,y
        coordinates.append((x, y))

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def show_object():
    with open('speed_markings.pkl', 'rb') as inp:
        txt = pickle.load(inp)
        print(txt)

cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)
while(1):
    cv2.imshow('image', img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        break
    elif k == ord('a'):
        # print(mouseX, mouseY)
        # print(coordinates)
        if len(coordinates) == 2:
            save_object(coordinates, 'speed_markings.pkl')
            print(coordinates)
        else:
            save_object(coordinates, 'roi_markings.pkl')
            print(coordinates)
        # show_object()
