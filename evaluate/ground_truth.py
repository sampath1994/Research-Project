import pickle
import cv2

with open('gt_data.pkl', 'rb') as f:
    data = pickle.load(f, encoding='latin1')
SAVE_VIDEO = False
dest = "C:/Users/promod/Desktop/researchPapers/yolo-object-detection/evaluate/test.avi"
cap = cv2.VideoCapture('C:/Users/promod/Desktop/researchPapers/yolo-object-detection/videos/overpass3.mp4')
frame_number = 0
writer = None
while cap.isOpened():
    ret, frame = cap.read()
    text = ""
    for car in data["cars"]:
        if car["valid"]:
            carNo = car["carId"]
            start = float(car["intersections"][0]["videoTime"])
            end = float(car["intersections"][1]["videoTime"])
            lane = car["laneIndex"]
            speed = car["speed"]
            time = frame_number / 50
            if (start<time) and (time<end):
                text = text + "car:"+str(carNo)+" speed:"+str(round(speed))+" Lane:"+str(lane) + "      "
    cv2.putText(frame, text, (20, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    frame_number = frame_number + 1
    if SAVE_VIDEO:
        # check if the video writer is None
        if writer is None:
            # initialize our video writer
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(dest, fourcc, 50,
                                     (frame.shape[1], frame.shape[0]), True)
        # write the output frame to disk
        writer.write(frame)
if SAVE_VIDEO:
    writer.release()
cap.release()
cv2.destroyAllWindows()