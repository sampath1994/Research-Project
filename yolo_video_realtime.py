# USAGE
# python yolo_video.py --input videos/airport.mp4 --output output/airport_output.avi --yolo yolo-coco

# import the necessary packages
import numpy as np
import argparse
import imutils
import time
import cv2
import os
from measure import calc_vehicle_len, count_vehicles
from graph import draw_ratio_graph
from sort import *
from mean_speed import get_mean_speed, get_each_mean_speed

mot_tracker = Sort()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
                help="path to input video")
ap.add_argument("-o", "--output", required=True,
                help="path to output video")
ap.add_argument("-y", "--yolo", required=True,
                help="base path to YOLO directory")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
                help="minimum probability to filter weak detections")
ap.add_argument("-t", "--threshold", type=float, default=0.3,
                help="threshold when applyong non-maxima suppression")
args = vars(ap.parse_args())

# load the COCO class labels our YOLO model was trained on
labelsPath = os.path.sep.join([args["yolo"], "coco.names"])
LABELS = open(labelsPath).read().strip().split("\n")

# initialize a list of colors to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
                           dtype="uint8")

# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.sep.join([args["yolo"], "yolov3.weights"])
configPath = os.path.sep.join([args["yolo"], "yolov3.cfg"])
FRAMES = 5
CAR_LEN = 350  # Actual car length in centimeters
MIN_BB_HEIGHT = 10
TRAIN = True
mean_interval = 12  # Frame interval of showing mean speed
current_mean_speed = 0
SAVE_VIDEO = False
FRAME_RATE = 30

# load our YOLO object detector trained on COCO dataset (80 classes)
# and determine only the *output* layer names that we need from YOLO
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# initialize the video stream, pointer to output video file, and
# frame dimensions
vs = cv2.VideoCapture(args["input"])
writer = None
(W, H) = (None, None)

# try to determine the total number of frames in the video file
try:
    prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
        else cv2.CAP_PROP_FRAME_COUNT
    total = int(vs.get(prop))
    print("[INFO] {} total frames in video".format(total))

# an error occurred while trying to determine the total
# number of frames in the video file
except:
    print("[INFO] could not determine # of frames in video")
    print("[INFO] no approx. completion time can be provided")
    total = -1

detection_buff = [None]*FRAMES
count = 0
ratio_list = []
speed_list = []
total_speed_list = []
frame_count = 0
class_id_list = []

# loop over frames from the video file stream
while True:
    # read the next frame from the file
    (grabbed, frame) = vs.read()

    # if the frame was not grabbed, then we have reached the end
    # of the stream
    if not grabbed:
        break

    # if the frame dimensions are empty, grab them
    if W is None or H is None:
        (H, W) = frame.shape[:2]

    # construct a blob from the input frame and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes
    # and associated probabilities
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()

    # initialize our lists of detected bounding boxes, confidences,
    # and class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability)
            # of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > args["confidence"]:
                # scale the bounding box coordinates back relative to
                # the size of the image, keeping in mind that YOLO
                # actually returns the center (x, y)-coordinates of
                # the bounding box followed by the boxes' width and
                # height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top
                # and and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates,
                # confidences, and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping
    # bounding boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
                            args["threshold"])
    mot_before_list = []
    # ensure at least one detection exists
    if len(idxs) > 0:
        # detection_count = len(idxs.flatten())
        # mot_before = np.arange(detection_count * 5).reshape(detection_count, 5)
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            # draw a bounding box rectangle and label on the frame
            color = [int(c) for c in COLORS[classIDs[i]]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.circle(frame, (int(x+w/2), int(y+h/2)), 5, (0, 0, 255), -1)
            # car tracking - start
            # mot_before[i] = [x, y, x+w, y+h, confidences[i]]
            # mot_before_list.append([x, y, x+w, y+h, confidences[i]])
            # car tracking - end
            text = "{}: {:.4f}".format(LABELS[classIDs[i]],
                                       confidences[i])
            cv2.putText(frame, text, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            class_id_list.append(classIDs[i])  # cleaned class id list
            if TRAIN:
                if LABELS[classIDs[i]] == 'car' and h > MIN_BB_HEIGHT:
                    mot_before_list.append([x, y, x + w, y + h, confidences[i]])
            else:
                if h > MIN_BB_HEIGHT:
                    mot_before_list.append([x, y, x + w, y + h, confidences[i]])
    count_vehicles(class_id_list, frame)
    class_id_list = []
    mot_before_np = np.array(mot_before_list)
    track_bbs_ids = mot_tracker.update(mot_before_np)
    # print(track_bbs_ids)
    mot_x1, mot_y1, mot_x2, mot_y2, obj_id = [0,0,0,0,0]
    for i in track_bbs_ids:
        mot_x1, mot_y1, mot_x2, mot_y2, obj_id = i
        x1_i = int(mot_x1)
        y1_i = int(mot_y1)
        x2_i = int(mot_x2)
        y2_i = int(mot_y2)
        cv2.rectangle(frame, (x1_i, y1_i), (x2_i, y2_i), (0,255,0), 2)
        text = str(obj_id)
        cv2.putText(frame, text, (x1_i, y1_i - 7),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    if count == FRAMES:
        count = 0
        if TRAIN:
            ratio_list.extend(calc_vehicle_len(detection_buff, frame, CAR_LEN, TRAIN))
        else:
            speed_list.extend(calc_vehicle_len(detection_buff, frame, CAR_LEN, TRAIN))

    detection_buff[count] = track_bbs_ids
    count = count + 1
    frame_count = frame_count + 1
    print("Seconds : "+str(frame_count / FRAME_RATE))
    if (frame_count % mean_interval) == 0:
        current_mean_speed = get_mean_speed(speed_list)
        total_speed_list.extend(speed_list)
        speed_list = []
    m_speed_text = "Mean speed : " + str(current_mean_speed)
    cv2.putText(frame, m_speed_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow('frame', frame)
    if cv2.waitKey(33) & 0xFF == ord('q'):
        break
    if SAVE_VIDEO:
        # check if the video writer is None
        if writer is None:
            # initialize our video writer
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, FRAME_RATE,(frame.shape[1], frame.shape[0]), True)

            # some information on processing single frame
            if total > 0:
                elap = (end - start)
                print("[INFO] single frame took {:.4f} seconds".format(elap))
                print("[INFO] estimated total time to finish: {:.4f}".format(elap * total))

        # write the output frame to disk
        writer.write(frame)
# print(ratio_list)
if TRAIN:
    draw_ratio_graph(ratio_list)
else:
    print("Speed List")
    print(speed_list)
print("Total mean speed list for each vehicle")
print(get_each_mean_speed(total_speed_list))
# release the file pointers
print("[INFO] cleaning up...")
if SAVE_VIDEO:
    writer.release()
vs.release()
