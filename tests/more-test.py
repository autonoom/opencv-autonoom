import cv2
import numpy as np
import time
import math


def draw_lines(img, lines):
    lijn1 = None
    lijn2 = None
    # print lines
    try:
        if lijn2 is None:
            for line in lines:
                if lijn1 is None:
                    coords = line[0]
                    print coords[0]
                elif lijn2 is None and (coords[0] < lijn1[0] -100 or coords[0] > lijn1[0] + 100):
                    coords = line[0]
                    print coords[0]
                if lijn1 is None:
                    lijn1 = coords
                elif lijn2 is None and lijn1 is not None:
                    lijn2 = coords
                cv2.line(img, (lijn1[0], lijn1[1]), (lijn1[2], lijn1[3]), [0, 255, 0], 3)
                if lijn2 is not None:
                    cv2.line(img, (lijn2[0], lijn2[1]), (lijn2[2], lijn2[3]), [0, 255, 0], 3)
                print coords
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
    cv2.line(img, ((x / 2),y),((x/2), y-200),[85, 26, 139],3)



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
    return original_image


img = cv2.imread("weg.png")
draw_middle(img)
new_screen = process_img(img)
cv2.imshow('window', new_screen)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()

