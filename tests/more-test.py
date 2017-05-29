import cv2
import numpy as np
import time
import math

centerPic = 350

def draw_lines(img, lines):
    lijn1 = None
    lijn2 = None
    i = 0
    try:
        while lijn1 is None and lijn2 is None:
            #eerste lijn en die moet onder de 350 pixels met de x1 en x2
            #eerste lijn niet twee keer vullen
            if lijn1 is None:
                a = i
                if lines[i][0][0] < centerPic and lines[i][0][2] < centerPic:
                    lijn1 = lines[i][0]
                    print "dit is lijn1"
                    print lijn1
                    a += 1

            #tweede lijn moet boven de 350 pixels met beide x1 en x2
            #tweede lijn niet opnieuw vullen
            if lijn2 is None:
                if lines[a][0][0] >= centerPic and lines[a][0][2] >= centerPic:
                    lijn2 = lines[a][0]
                    print "dit is lijn2"
                    print lijn2
            i += 1
            #elif lijn2 is None or (coords[0] < lijn1[0] -100 or coords[0] > lijn1[0] + 100):
            #    coords = line[0]
            #if lijn1 is None:
            #    lijn1 = coords
            #elif lijn2 is None and lijn1 is not None:
            #    lijn2 = coords

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


def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    processed_img = cv2.GaussianBlur(processed_img, (3, 3), 0)

    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, np.array([]), 20, 5)
    draw_lines(original_image, lines)
    draw_middle(img)
    return original_image


img = cv2.imread("weg.png")

new_screen = process_img(img)
cv2.imshow('window', new_screen)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()

