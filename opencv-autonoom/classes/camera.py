import numpy as np
import cv2
import time
import math
import urllib


def draw_lines(img, lines):
    lijn1 = None
    lijn2 = None
    # print lines
    try:
        if lijn2 is None:
            for line in lines:
                if lijn1 is None:
                    coords = line[0]
                elif lijn2 is None or (coords[0] < lijn1[0] -100 or coords[0] > lijn1[0] + 100):
                    coords = line[0]
                if lijn1 is None:
                    lijn1 = coords
                elif lijn2 is None and lijn1 is not None:
                    lijn2 = coords
                cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 3)
                if lijn2 is not None:
                    cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)
        xtop = (lijn2[0] + lijn1[2]) / 2
        xbot = (lijn2[2] + lijn1[0]) / 2
        cv2.line(img,(xtop, 0), (xbot, 400),[255, 140, 0], 3)
        print xtop
        print xbot

        calculate_degree(lijn1)
        calculate_degree(lijn2)
    except Exception:
        pass


def draw_middle(img):
    y, x, z = img.shape
    cv2.line(img, ((x / 2), y), ((x/2), y-50), [85, 26, 139], 3)



def calculate_degree(point):                     # http://wikicode.wikidot.com/get-angle-of-line-between-two-points
    x_diff = point[2] - point[0]
    y_diff = point[3] - point[1]
    angle = math.degrees(math.atan2(y_diff, x_diff))
    angle = angle * -1
    print round(angle % 360)


def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked


def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    processed_img = cv2.GaussianBlur(processed_img, (3, 3), 0)
    vertices = np.array([[0, 400], [0, 200], [300, 200], [500, 200], [800, 200], [800, 400]], np.int32)
    processed_img = roi(processed_img, [vertices])
    #                       edges
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, np.array([]), 50, 15)
    print 'dit is lijn '
    print\
        lines
    draw_lines(original_image, lines)
    return processed_img


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
            new_screen = process_img(frame)
           # print('Loop took {} fps' .format(1 / (time.time()-last_time)))
            last_time = time.time()
            cv2.imshow('window', new_screen)
            # cv2.imshow('wiqndow2', cap)
            cv2.imshow('window2', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
main()
