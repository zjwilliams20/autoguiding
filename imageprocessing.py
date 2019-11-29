##############################################################################
#                               imageprocesing.py                            #
##############################################################################

import numpy as np
import cv2

##############################################################################
def filter_img(img, lower_thresh):
    """Convert to grayscale, binary threshold, and return binary image"""
    upper_thresh = 255

    # additional optional filters
    #kernel = np.ones((5, 5), np.uint8)
    #close = cv2.morphologyEx(gray_img, cv2.MORPH_CLOSE, kernel)
    #denoised = cv2.fastNlMeansDenoising(close, h=10, templateWindowSize=7, searchWindowSize=21)

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binary_img = cv2.threshold(gray_img, lower_thresh, upper_thresh, 0)

    return binary_img

##############################################################################
def find_centroids(img, lower_thresh):
    """Locate centroids of a filtered img and store into a list. Keep track
    of stars that weren't caught in findContours (tiny_stars) to optimize
    future thresholding."""

    binary = filter_img(img, lower_thresh)

    contours, hierarchy = cv2.findContours(
        image=binary,
        mode=cv2.RETR_EXTERNAL,
        method=cv2.CHAIN_APPROX_SIMPLE)
    centroids = np.zeros((len(contours), 2), dtype="int")

    recolor_img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    tiny_stars = 0
    for idx, contour in enumerate(contours):
        m = cv2.moments(contour)

        if m['m00'] != 0:
            (cX, cY) = (round(m['m10'] / m['m00']), round(m['m01'] / m['m00']))
            centroids[idx] = (cX, cY)
            #cv2.drawMarker(binary, (cX, cY), 255)
        else:
            tiny_stars += 1

    # print(f"tiny_stars = {tiny_stars}")
    return centroids, recolor_img
