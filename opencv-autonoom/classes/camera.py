import numpy as np
import cv2
import time
import math
import urllib
import socket



def draw_lines(img, lines):
    lijn1 = None
    lijn2 = None

    i = 0
    # print lines
    centerpic = 300

    try:
        while (lijn1 is None and lijn2 is None):
            # eerste lijn en die moet onder de 300 pixels met de x1 en x2
            # eerste lijn niet twee keer vullen
            if lijn1 is None:
                if lijn2 is None:
                    a = i
                if lines[i][0][0] < centerpic and lines[i][0][2] < centerpic:
                    lijn1 = lines[i][0]
                    cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 3)
                    a += 1
                    # print "dit is lijn1"
                    # print lijn1
            # tweede lijn moet boven de 300 pixels met beide x1 en x2
            # tweede lijn niet opnieuw vullen
            if lijn2 is None:
                if lines[a][0][0] >= centerpic and lines[a][0][2] >= centerpic:
                    lijn2 = lines[a][0]
                    cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)
                    # print "dit is lijn2"
                    # print lijn2
            i += 1

        xtop = (lijn2[0] + lijn1[2]) / 2
        xbot = (lijn2[2] + lijn1[0]) / 2
        # cv2.line(img,(xtop, 0), (xbot, 400),[255, 140, 0], 3)
        # cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)
        gem = (xtop + xbot) / 2
        # print gem
        draw_middle(img, gem)
        cv2.line(img,(gem, 0), (gem, 400),[255, 140, 0], 3)


    except Exception:
        pass


def draw_middle(img, gem):
    y, x, z = img.shape
    dif = gem - (x / 2)
    TCP_IP = '192.168.42.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(dif)
    print dif
    cv2.line(img, ((x / 2), y), ((x/2), y-50), [85, 26, 139], 1)



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
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, np.array([]), 30, 50)
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
