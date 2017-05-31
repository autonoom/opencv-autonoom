import numpy as np
import cv2
import time
import urllib


face_cascade = cv2.CascadeClassifier('face.xml')
eye_cascade = cv2.CascadeClassifier('eye.xml')

# this is the cascade we just made. Call what you want
watch_cascade = cv2.CascadeClassifier('cascade.xml')

def reconTrafficLight(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # add this
    # image, reject levels level weights.
    watches = watch_cascade.detectMultiScale(gray, 30, 30)

    # add this
    for (x, y, w, h) in watches:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)


    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    return img

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
            new_screen = reconTrafficLight(frame)
           # print('Loop took {} fps' .format(1 / (time.time()-last_time)))
            last_time = time.time()
            cv2.imshow('window', new_screen)
            # cv2.imshow('wiqndow2', cap)
            cv2.imshow('window2', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
main()

