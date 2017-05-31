import numpy as np
import cv2
import time
import urllib


#face_cascade = cv2.CascadeClassifier('face.xml')
#eye_cascade = cv2.CascadeClassifier('eye.xml')

# this is the cascade we just made. Call what you want
detectMultiScale = cv2.CascadeClassifier('traffic_light.xml')


# class ObjectDetection(object):
#     def __init__(self):

#https://github.com/hamuchiwa/AutoRCCar/blob/master/computer/rc_driver.py
def detect(image):
    red_light = False
    green_light = False
    yellow_light = False
    # y camera coordinate of the target point 'P'
    v = 0

    # minimum value to proceed traffic light state validation
    threshold = 150

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detection
    cascade_obj = detectMultiScale.detectMultiScale(
        gray_image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # draw a rectangle around the objects
    for (x_pos, y_pos, width, height) in cascade_obj:
        cv2.rectangle(image, (x_pos + 5, y_pos + 5), (x_pos + width - 5, y_pos + height - 5), (255, 255, 255), 2)
        v = y_pos + height - 5

        # traffic lights

        roi = gray_image[y_pos + 10:y_pos + height - 10, x_pos + 10:x_pos + width - 10]
        mask = cv2.GaussianBlur(roi, (25, 25), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)

        # check if light is on
        if maxVal - minVal > threshold:
            cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)

            # Red light
            if 1.0 / 8 * (height - 30) < maxLoc[1] < 4.0 / 8 * (height - 30):
                cv2.putText(image, 'Red', (x_pos + 5, y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                red_light = True
                print "red"

            # Green light
            elif 5.5 / 8 * (height - 30) < maxLoc[1] < height - 30:
                cv2.putText(image, 'Green', (x_pos + 5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                            2)
                green_light = True
                print "green"
            #yellow light
            elif 4.0/8*(height-30) < maxLoc[1] < 5.5/8*(height-30):
                cv2.putText(image, 'Yellow', (x_pos+5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                yellow_light = True
                print "orange"
    return image


def main():
    last_time = time.time()
    stream = urllib.urlopen('http://192.168.42.1:5000/video_feed')
    bytes = ''
    while True:
        bytes += stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b + 2]
            bytes = bytes[b + 2:]
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
            new_screen = detect(frame)
           # print('Loop took {} fps' .format(1 / (time.time()-last_time)))
            last_time = time.time()

            # cv2.imshow('wiqndow2', cap)
            cv2.imshow('window2', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
main()

