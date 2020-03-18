##############################################################################
#                               imageprocesing.py                            #
##############################################################################

import numpy as np
import cv2
from PIL import Image, ImageTk

##############################################################################
def load_image(test, image_num):
    """Load a single image from a local directory, crop according to the camera size,
     and resize it to maximize it in the window."""

    # test images from PHD2 Simulation Program
    if test in ["test1", "test5", "test10"]:
        img = cv2.imread(f"C:/Users/ZachJW/Pictures/Camera Roll"
                         f"/Astrostuff/{test}/test{image_num}.png")
        # crop and resize image
        final = img[:550, :550]
        scaling_factor = 0.75
        #final = cv2.resize(crop, None, fx=scaling_factor, fy=scaling_factor,
                           #interpolation=cv2.INTER_LINEAR_EXACT)

    # test images from actual USB Camera
    elif test in ["alnilam", "lamp", "mirphak", "rigel"]:
        img = cv2.imread(f"C:/Users/ZachJW/PycharmProjects/autoguiding/"
                         f"samples/{test}/sample{image_num}.png")

        # crop frame to remove unncessary dark portion of casing
        crop = img[90:395, 165:470]

        # enlarge frame for greater pixel flexibility
        scaling_factor = 1.75
        final = cv2.resize(crop, None, fx=scaling_factor, fy=scaling_factor,
                           interpolation=cv2.INTER_LINEAR_EXACT)

    else:
        print(f"<WARNING: invalid pathname for test: {test}>")

    if img is None:
        print(f"<WARNING: image read failed>")

    return final

##############################################################################
def filter_img(img, lower_thresh):
    """Convert to grayscale, binary threshold, and return binary image"""

    upper_thresh = 255
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binary_img = cv2.threshold(gray_img, lower_thresh, upper_thresh, 0)

    return binary_img

##############################################################################
def find_centroids(img, lower_thresh):
    """Locate centroids of a filtered img and store into a list. Keep track
    of stars that weren't caught in findContours (tiny_stars) to optimize
    future thresholding."""

    img = filter_img(img, lower_thresh)

    # locate all stars with more than 4 pixels in a filtered image
    img, contours, hierarchy = cv2.findContours(
        image=img,
        mode=cv2.RETR_EXTERNAL,
        method=cv2.CHAIN_APPROX_SIMPLE)
    centroids = np.zeros((len(contours), 2), dtype="int")

    # Recolor image to allow coloration
    recolor_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Find the center of each of the contours and store into a list of centroids
    tiny_stars = 0
    for idx, contour in enumerate(contours):
        m = cv2.moments(contour)

        if m['m00'] != 0:
            (cX, cY) = (round(m['m10'] / m['m00']), round(m['m01'] / m['m00']))
            centroids[idx] = (cX, cY)
            # cv2.drawMarker(binary, (cX, cY), 255)
        else:
            tiny_stars += 1

    return centroids, recolor_img

##############################################################################
def markup_img(img, tracker):
    """Draw bounding circle and orthogonal axes on an image."""

    # draw rectangle around star being tracked for user
    if tracker.status.mode is tracker.LOCKED:
        tsCentroid = tracker.status.COM
        boxSize = 8
        cv2.rectangle(img, (tsCentroid[0] - boxSize, tsCentroid[1] - boxSize),
                      (tsCentroid[0] + boxSize, tsCentroid[1] + boxSize), (0, 150, 0), 1)

    orgX, orgY = tracker.orgX, tracker.orgY
    axes = cv2.line(img, (orgX, 0), (orgX, orgY * 2), color=(110, 0, 0))
    axes = cv2.line(axes, (0, orgY), (orgX * 2, orgY), color=(110, 0, 0))
    marked_img = cv2.circle(axes, (orgX, orgY), radius=orgY, color=(110, 0, 0))

    return marked_img

##############################################################################
def initial_img_load(tracker):
    """Load an image on the very first loadup of the GUI."""

    loaded_img = load_image("lamp", 4)
    filtered_img = filter_img(loaded_img, 100)
    colored_img = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
    marked_img = markup_img(colored_img, tracker)
    pil_img = Image.fromarray(marked_img)
    gui_img = ImageTk.PhotoImage(pil_img)
    return filtered_img, gui_img

##############################################################################
def load_logo():
    """Load the Astrothots logo into the GUI Application as a PIL Image
    (not implemented)."""

    initial_logo = cv2.imread("figures/astrothots.PNG")
    scaling_factor = 0.088
    resized_logo = cv2.resize(initial_logo, None, fx=scaling_factor, fy=scaling_factor,
                       interpolation=cv2.INTER_LINEAR_EXACT)
    pil_img = Image.fromarray(resized_logo)

    return ImageTk.PhotoImage(pil_img)
