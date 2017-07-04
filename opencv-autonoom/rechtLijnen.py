import math
import socket
import urllib
import cv2
import numpy as np

TCP_IP = '192.168.42.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

detectMultiScale = cv2.CascadeClassifier('traffic_light.xml')

#This function detects a traffic light it has been copied from the following link
#https://github.com/hamuchiwa/AutoRCCar/blob/master/computer/rc_driver.py
def detect_trafficlight(image):
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
                s.send('stop')
                print "red"

            # Green light
            elif 5.5 / 8 * (height - 30) < maxLoc[1] < height - 30:
                cv2.putText(image, 'Green', (x_pos + 5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                green_light = True
                s.send('start')
                print "green"
                return True

            #yellow light
            elif 4.0/8*(height-30) < maxLoc[1] < 5.5/8*(height-30):
                cv2.putText(image, 'Orange', (x_pos+5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                yellow_light = True

                # s.send('stop')
                print "orange"
    return False


def send():
    s.send('start')

def calculate_degree(point):  # http://wikicode.wikidot.com/get-angle-of-line-between-two-points
    x_diff = point[2] - point[0]
    y_diff = point[3] - point[1]
    angle = math.degrees(math.atan2(y_diff, x_diff))
    angle = angle * -1
    angle = round(angle % 360)
    return angle

def calc_lines(img, lines):
    lijn1 = None
    lijn2 = None
    i = 0

    try:
        while not (i is len(lines)):
            if calculate_degree(lines[i][0]) < 90:
                if lijn1 is None:
                    lijn1 = lines[i][0]
                else:
                    lijn1 = (lijn1 + lines[i][0]) / 2


            # tweede lijn moet boven de 300 pixels met beide x1 en x2
            # tweede lijn niet opnieuw vullen
            if calculate_degree(lines[i][0]) > 270:
                if lijn2 is None:
                    lijn2 = lines[i][0]
                else:
                    lijn2 = (lijn2 + lines[i][0]) / 2
            i += 1

        #make here a try for the avg
        #Otherwise he won't go further
        try:
            cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 0, 255], 2)
            cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 2)
        except:
            pass
        # ##turn to the right
        if lijn1 is not None and lijn2 is None:
            cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 2)  # Teken lijn 1
            # calculate degree
            check = calculate_degree(lijn1)
            # if calculate below 40 skip it
            # because he made's the turn to fast otherwise

            if check < 40:
                pass
            else:
                # this value is adapt to max or min value of the servo
                steeringvalue = (check*0.050)
                print 'check', check
                print 'steeringvalue', steeringvalue
        ## turn to the left
        elif lijn2 is not None and lijn1 is None:
            cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [255, 255, 255], 2)  # Teken lijn 2
            check = calculate_degree(lijn2)
            # 360 minus the degree because of the left turn
            check = 360-check
            # if calculate below 44 skip it
            # because he made's the turn to fast otherwise
            if check < 44:
                # this value is adapt to max or min value of the servo
                steeringvalue = (-(check*0.075))
                #send the value
                s.send(str(steeringvalue))
            else:
                pass
        else:
            # bereken gemiddelde van per lijn lijn

            xtop = (lijn2[0] + lijn1[2]) / 2
            xbot = (lijn2[2] + lijn1[0]) / 2

            # cv2.line(img,(xtop, 0), (xbot, 400),[255, 140, 0], 3)
            # cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)
            gem = (xtop + xbot) / 2  # berekent gemiddelde van de 2 lijnen

            middle(img, gem)
            #cv2.line(img, (gem, 0), (gem, 400), [255, 140, 0], 3)

    except Exception:
        pass


def middle(image, gem):
    y, x = image.shape
    dif = gem - (x / 2)
    # calculate the avg of the two lines he find
    if calculate_avg(dif):
        pass
    else:
        pass
    cv2.line(image, ((x / 2), y), ((x / 2), y - 50), [85, 26, 139], 1)

# these variables are for the calculation of the avg function
counter = 0
counter2 = 0
data = 0
data2 = 0

#This function takes the avg of multiple lines
#For the simple reason that the servo didn't went to fast to left and right.
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
            data2 = data2 / (avg1*avg2)
            #the 0.9 is to transform a correct data for the servo
            data2 *= 0.9
            print "Avg data = " + str(data2)
            s.send(str(data2))
            data = 0
            counter = 0
            data2 = 0
            counter2 = 0
            return True
    else:
        print 'failed avg'
    return False


def find_lines(original_image):
    #                                                                   linelenght
    #                                                                         \/  gaps
    lines = cv2.HoughLinesP(original_image, 1, np.pi / 180, 180, np.array([]), 20, 50)
    # this function takes the image and search for lines and turns
    calc_lines(original_image, lines)
    return original_image

def roi(img):
    # take the width and the height
    height, width = img.shape
    ########################################
    # (0.0)                        (300.300)#
    #                                      #
    #                                      #
    #                                      #
    #                                      #
    # (0.300)                      (300.300)#
    ########################################
    #        [y1:y2, x1, x2] <-- this is the region of interest
    img = img[height - 250:height, width - width:width]
    return img

def image_retrieved_and_edited(img):
    #convert color (BRG) img to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #the Canny function with threshold
    img = cv2.Canny(img, threshold1=180, threshold2=280)
    #the GaussianBlur blurred the image
    img = cv2.GaussianBlur(img, (3, 3), 0)
    #The region of interest is used to minimize the interest of the image
    img = roi(img)
    return img

def main():
    # https://github.com/miguelgrinberg/flask-video-streaming
    Traffic = False
    stream = urllib.urlopen('http://192.168.42.1:5000/video_feed')  # haalt video stream op
    bytes = ''

    while True:
        bytes += stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b + 2]
            bytes = bytes[b + 2:]
            #take a frame from flask
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            #edit the frame
            img_edit = image_retrieved_and_edited(frame)
            #find the lines
            new_screen = find_lines(img_edit)
            if not Traffic:
                trafficlight = detect_trafficlight(frame)
                if trafficlight == True:
                    Traffic = True
            else:
                pass
            #show the lines and average
            cv2.imshow('traffic light', trafficlight)
            cv2.imshow('lijnen', new_screen)
            if cv2.waitKey(25) & 0xFF == ord('q'):  # when 'q' is pressed the program will stop
                cv2.destroyAllWindows()
main()      