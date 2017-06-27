import math
import socket
import urllib
import cv2
import numpy as np

detectMultiScale = cv2.CascadeClassifier('traffic_light.xml')

TCP_IP = '192.168.42.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

s.send('start')

# def detect_trafficlight(image):
#
#     red_light = False
#     green_light = False
#     yellow_light = False
#     # y camera coordinate of the target point 'P'
#     v = 0
#
#     # minimum value to proceed traffic light state validation
#     threshold = 150
#
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#     # detection
#     cascade_obj = detectMultiScale.detectMultiScale(
#         gray_image,
#         scaleFactor=1.1,
#         minNeighbors=5,
#         minSize=(30, 30)
#     )
#
#     # draw a rectangle around the objects
#     for (x_pos, y_pos, width, height) in cascade_obj:
#         cv2.rectangle(image, (x_pos + 5, y_pos + 5), (x_pos + width - 5, y_pos + height - 5), (255, 255, 255), 2)
#         v = y_pos + height - 5
#
#         # traffic lights
#
#         roi = gray_image[y_pos + 10:y_pos + height - 10, x_pos + 10:x_pos + width - 10]
#         mask = cv2.GaussianBlur(roi, (25, 25), 0)
#         (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)
#
#         # check if light is on
#         if maxVal - minVal > threshold:
#             cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)
#
#             # Red light
#             if 1.0 / 8 * (height - 30) < maxLoc[1] < 4.0 / 8 * (height - 30):
#                 cv2.putText(image, 'Red', (x_pos + 5, y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
#                 red_light = True
#                 s.send('stop')
#                 print "red"
#
#             # Green light
#             elif 5.5 / 8 * (height - 30) < maxLoc[1] < height - 30:
#                 cv2.putText(image, 'Green', (x_pos + 5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#                 green_light = True
#                 s.send('start')
#                 print "green"
#
#             #yellow light
#             elif 4.0/8*(height-30) < maxLoc[1] < 5.5/8*(height-30):
#                 cv2.putText(image, 'Orange', (x_pos+5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
#                 yellow_light = True
#                 # TCP_IP = '192.168.42.1'
#                 # TCP_PORT = 5005
#                 # BUFFER_SIZE = 1024
#                 # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 # s.connect((TCP_IP, TCP_PORT))
#                 # s.send('stop')
#                 print "orange"
#     return image


def draw_lines(img, lines):
    lijn1 = None
    lijn2 = None
    i = 0

    # print lines
    # centerpic = 300
    try:
        while not (i is len(lines)):
            # eerste lijn en die moet onder de 300 pixels met de x1 en x2
            # eerste lijn niet twee keer vullen

            # print lines[i][0]
            if calculate_degree(lines[i][0]) < 90:
                if lijn1 is None:
                    lijn1 = lines[i][0]
                else:
                    lijn1 = (lijn1 + lines[i][0]) / 2

                    # print "dit is lijn1"
                    # print lijn1
            # tweede lijn moet boven de 300 pixels met beide x1 en x2
            # tweede lijn niet opnieuw vullen
            if calculate_degree(lines[i][0]) > 270:
                if lijn2 is None:
                    lijn2 = lines[i][0]
                else:
                    lijn2 = (lijn2 + lines[i][0]) / 2

                    #print "dit is lijn2"
                    #print lijn2
            i += 1
        cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 0, 255], 2)
        cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 2)
        # if lijn1 is not None and lijn2 is None:
        #     cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 2)  # Teken lijn 1
        #     check = calculate_degree(lijn1)
        #     check = 360 - check
        #     check /= 3
        #     print 'klaas1'
        #     print check
        #     s.send(str(check))
        if lijn2 is not None and lijn1 is None:
            cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 0, 255], 2)  # Teken lijn 2
            check = calculate_degree(lijn2)
            check -= 300
            steeringvalue = (check*0.05)+13,4
            print check
            print steeringvalue
            s.send(str(steeringvalue))

        # bereken gemiddelde van per lijn lijn
        xtop = (lijn2[0] + lijn1[2]) / 2
        xbot = (lijn2[2] + lijn1[0]) / 2
        # cv2.line(img,(xtop, 0), (xbot, 400),[255, 140, 0], 3)
        # cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)
        gem = (xtop + xbot) / 2  # berekent gemiddelde van de 2 lijnen
        # print gem
        draw_middle(img, gem)
        cv2.line(img, (gem, 0), (gem, 400), [255, 140, 0], 3)

    except Exception:
        pass


def draw_middle(image, gem):
    y, x, z = image.shape
    dif = gem - (x / 2)
    # print dif
    cv2.line(image, ((x / 2), y), ((x / 2), y - 50), [85, 26, 139], 1)


# dit is code om de hoek te bepalen van de lijnen dit gebruiken wij niet
def calculate_degree(point):  # http://wikicode.wikidot.com/get-angle-of-line-between-two-points
    x_diff = point[2] - point[0]
    y_diff = point[3] - point[1]
    angle = math.degrees(math.atan2(y_diff, x_diff))
    angle = angle * -1
    angle = round(angle % 360)
    # print angle
    return angle


counter = 0
counter2 = 0
data = 0
data2 = 0


def calculate_avg(diference):
    global counter
    global counter2
    global data, data2

    avg1 = 2
    avg2 = 5
    if counter < avg1:
        counter += 1
        data += float(diference)
    elif counter is avg1:
        # avg from avg
        data = data / avg1
        if counter2 < avg2:
            counter2 += 1
            data2 += data
        elif counter2 is avg2:
            data2 = float(data2)
            data2 = data2 / avg2
            data2 = data2 / 10
            data2 *= 0.5
            data2 = (4.2 * data2) + 13.4
            print "Avg data = " + str(data2)
            s.send(str(data2))
            data = 0
            counter = 0
            data2 = 0
            counter2 = 0
            return True
    else:
        print 'dd'
    return False


# def bird_eye(image):
#     # y, x, ch = image.shape
#     # print x
#     # print y
#     src = np.float32([[0, 140], [480, 140], [480, 360], [0, 360]])
#     dst = np.float32([[0, 0], [480, 0], [300, 450], [180, 450]])
#     M = cv2.getPerspectiveTransform(src, dst)
#     warped_image = cv2.warpPerspective(image, M, (640, 480))
#     cv2.imshow('transform', warped_image)

# maakt region of interest aan


def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked


def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    processed_img = cv2.GaussianBlur(processed_img, (3, 3), 0)
    vertices = np.array([[0, 400], [50, 250], [150, 250], [500, 250], [800, 250], [800, 400]], np.int32)
    processed_img = roi(processed_img, [vertices])
    #                       edges
    #                                                                   linelenght
    #                                                                         \/  gaps
    lines = cv2.HoughLinesP(processed_img, 1, np.pi / 180, 180, np.array([]), 10, 50)
    draw_lines(original_image, lines)

    # cv2.imshow('sjaak', original_image)         # stuurt de foto en de coordinaten van de lijnen op
    return processed_img


def main():
    # https://github.com/miguelgrinberg/flask-video-streaming
    stream = urllib.urlopen('http://192.168.42.1:5000/video_feed')  # haalt video stream op
    bytes = ''
    while True:
        bytes += stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b + 2]
            bytes = bytes[b + 2:]
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            # new2_screen = detect_trafficlight(frame)
            new_screen = process_img(frame)  # stuurt frame op naar process_img
            cv2.imshow('window', new_screen)  # laat video zien
            # cv2.imshow('window2', new2_screen)
            # cv2.imshow('wiqndow2', cap)
            cv2.imshow('window3', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):  # wanneer 'q' is ingedrukt stop programma
                cv2.destroyAllWindows()
                break


main()
