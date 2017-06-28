import cv2
import numpy as np


img = cv2.imread('watch.jpg', cv2.IMREAD_GRAYSCALE)
height, width = img.shape
########################################
#(0.0)                        (300.300)#
#                                      #
#                                      #
#                                      #
#                                      #
#(0.300)                      (300.300)#
########################################
#        [y1:y2, x1, x2]
img = img[height-100:height, width-width:width]
cv2.imshow('image', img)


cv2.waitKey(0)
cv2.destroyAllWindows()

