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
                if lines[i][0][0] < centerpic and lines[i][0][2] < centerpic:                   # als de x-coördinaat onder de 300 pixels ligt dan is dat lijn 1
                    lijn1 = lines[i][0]
                    cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 3) # Teken lijn 1
                    a += 1
                    # print "dit is lijn1"
                    # print lijn1
            # tweede lijn moet boven de 300 pixels met beide x1 en x2
            # tweede lijn niet opnieuw vullen
            if lijn2 is None:
                if lines[a][0][0] >= centerpic and lines[a][0][2] >= centerpic:             # als de x-coördinaat boven de 300 pixels ligt dan is dat lijn 2
                    lijn2 = lines[a][0]
                    cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)   # teken lijn 2
                    # print "dit is lijn2"
                    # print lijn2
            i += 1
            # bereken gemiddelde van per lijn lijn
        xtop = (lijn2[0] + lijn1[2]) / 2
        xbot = (lijn2[2] + lijn1[0]) / 2
        # cv2.line(img,(xtop, 0), (xbot, 400),[255, 140, 0], 3)
        # cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)
        gem = (xtop + xbot) / 2         # berekent gemiddelde van de 2 lijnen
        # print gem
        draw_middle(img, gem)
        cv2.line(img,(gem, 0), (gem, 400),[255, 140, 0], 3)


    except Exception:
        pass

    # hier word het verschil berekent tussen het midden van de camera en het gemiddelde van de twee lijnen
def draw_middle(img, gem):
    y, x, z = img.shape
    dif = gem - (x / 2)

    # hier wordt her verschil van het gemiddelde en het midden van de camera opgestuurd via telnet
    TCP_IP = '192.168.42.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(dif)
    print dif
    cv2.line(img, ((x / 2), y), ((x/2), y-50), [85, 26, 139], 1)


# dit is code om de hoek te bepalen van de lijnen dit gebruiken wij niet
def calculate_degree(point):                     # http://wikicode.wikidot.com/get-angle-of-line-between-two-points
    x_diff = point[2] - point[0]
    y_diff = point[3] - point[1]
    angle = math.degrees(math.atan2(y_diff, x_diff))
    angle = angle * -1
    print round(angle % 360)

                                                                # maakt region of interest aan
def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked


def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)                                        # maakt van de originele image een GRAY scale foto
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)                                # laat de buitenste lijnen zien van een object
    processed_img = cv2.GaussianBlur(processed_img, (3, 3), 0)                                              # blur die image!!!
    vertices = np.array([[0, 400], [0, 200], [300, 200], [500, 200], [800, 200], [800, 400]], np.int32)     # bepaal de region of interest
    processed_img = roi(processed_img, [vertices])
    #                       edges
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, np.array([]), 30, 50)                         # berekent lijnen van de image door houghlineP
    draw_lines(original_image, lines)                                                                       # stuurt de foto en de coordinaten van de lijnen op
    return processed_img


def main():
    last_time = time.time()                             # https://github.com/miguelgrinberg/flask-video-streaming
    stream = urllib.urlopen('http://192.168.42.1:5000/video_feed')                                          # haalt video stream op
    bytes = ''
    while True:
        bytes += stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b + 2]
            bytes = bytes[b + 2:]
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)           # frame is een frame van de video stream
            new_screen = process_img(frame)                                                     # stuurt frame op naar process_img
           # print('Loop took {} fps' .format(1 / (time.time()-last_time)))
            last_time = time.time()
            cv2.imshow('window', new_screen)                                        # laat video zien
            # cv2.imshow('wiqndow2', cap)
            cv2.imshow('window2', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):                              # wanneer 'q' is ingedrukt stop programma
                cv2.destroyAllWindows()
                break
main()
