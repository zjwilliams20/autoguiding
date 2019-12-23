##############################################################################
#                                   autoguiding.py                           #
##############################################################################


import cv2
import centroidtracker as ct
import imageprocessing as imgproc
import controller as con
import camera as cam
import gui

from logging import FileHandler
from vlogging import VisualRecord
import logging

##############################################################################
def setup_logger():
    # open the logging file
    logger = logging.getLogger("visual_logging_example")
    fh = FileHandler("log.html", mode="w")

    # set the logger attributes
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger

##############################################################################
def record(logger, images, text):
    logger.debug(VisualRecord(text, images, fmt="png"))
    return logger

##############################################################################
def sample_capture(count):
    Cam = cam.Camera()
    print("Beginning sample capture...")
    for i in range(count):
        print(f"\tSample {i}")
        img = Cam.capture()
        img_name =  f"sample.png"
        cv2.imshow(gui.win_name, img)
        cv2.waitKey(500)
        cv2.imwrite(img_name, img)

##############################################################################
def load_image(test, image_num, tracker):
    """Load a single image from a directory, crop according to the camera size,
     and resize it to maximize it in the window."""

    # test images from PHD2 Simulation Program
    if test in ["test1", "test5", "test10"]:
        img = cv2.imread(f"C:/Users/ZachJW/Pictures/Camera Roll"
                         f"/Astrostuff/{test}/test{image_num}.png")
        # cropping and resizing unnecessary
        final = img

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
        print(f"<ERR: invalid pathname for test: {test}>")
        exit()

    if img is None:
        print(f"<ERR: image read failed>")
        exit()

    return final

##############################################################################
def markup_img(img, tracker):
    """Draw bounding circle and orthogonal axes on an image."""

    # draw rectangle around star being tracked for user
    if tracker.mode is tracker.LOCKED:
        (tsID, tsCentroid) = tracker.getTrackStar()
        boxSize = 8
        cv2.rectangle(img, (tsCentroid[0] - boxSize, tsCentroid[1] - boxSize),
                      (tsCentroid[0] + boxSize, tsCentroid[1] + boxSize), (0, 150, 0), 1)

    orgX, orgY = tracker.orgX, tracker.orgY
    axes = cv2.line(img, (orgX, 0), (orgX, img.shape[1]), color=(0, 0, 110))
    axes = cv2.line(axes, (0, orgY), (img.shape[0], orgY), color=(0, 0, 110))
    marked_img = cv2.circle(axes, (orgX, orgY), radius=orgY, color=(0, 0, 110))

    return marked_img

##############################################################################
def single_run(test, img_num, logger, lower_thresh=10):
    """Run a simulation on a single image to assess the filtering, centroid
    calculation, and autoselect features in a more isolated context."""

    print("Beginning program... Press any key to advance. Double click to exit.")
    Tracker = ct.CentroidTracker()
    Controller = con.Controller()
    #Camera = cam.Camera()
    Win = gui.setup()

    # load image from camera capture or directory
    initial_img = load_image(test, img_num, Tracker)
    record(logger, initial_img, "Initial")
    #initial_img = Camera.capture()

    cv2.imshow(gui.win_name, initial_img)
    print("\t<image loaded>")
    cv2.waitKey(-1)

    # locate centroids and return binary image
    Centroids, bin_img = imgproc.find_centroids(initial_img, lower_thresh)
    record(logger, bin_img, "Binary")

    cv2.imshow(gui.win_name, bin_img)
    print("\t<centroids located>")
    cv2.waitKey(-1)

    # generate x and y error and update the Tracker to reflect the current centroids
    dX, dY = Tracker.update(Centroids)

    # calculate the x and y motor rates from the PI Controller
    xRate, yRate = Controller.calculate(dX, dY)
    print(f"\t<xRate = {xRate} // yRate = {yRate}")

    # autoselect a star and markup image
    autosel_img = Tracker.autoselect(bin_img)
    marked_img = markup_img(autosel_img, Tracker)
    record(logger, marked_img, "Marked")

    cv2.imshow(gui.win_name, marked_img)
    print("\t<trackStar selected>")
    cv2.waitKey(-1)

    #record(logger, [initial_img, bin_img, marked_img], "1. Initial 2. Binary 3. Marked")

    cv2.destroyWindow(Win)

##############################################################################
def multiple_run(test, logger, lower_thresh=10):
    """Run a tracking simulation on a folder containing 10 images."""

    print("Beginning program... Double click to exit.")
    Window = gui.setup()   # setup viewing window
    Tracker = ct.CentroidTracker()  # setup CentroidTracker
    Controller = con.Controller()
    #Camera = cam.Camera()

    # iterate through 10 images in the target directory
    for i in range(10):

        Initial_Img = load_image(test, i, Tracker)   # load image from test directory
        #Initial_Img = Camera.capture()     # capture frame from USB Camera

        # locate the centroids as a list of (x, y) tuples and get binary thresholded image
        Centroids, Filtered_Img = imgproc.find_centroids(Initial_Img, lower_thresh)

        # update the Tracker object for the next list of input centroids
        dX, dY = Tracker.update(Centroids)
        xRate, yRate = Controller.calculate(dX, dY)
        print(f"\t\txRate: {xRate}\n\t\tyRate: {yRate}")

        # if the status is SEARCHING, autoselect a guide star
        if Tracker.mode is Tracker.SEARCHING:
            # get a guide star and return image with smallest bounding rectangle
            Autosel_Img = Tracker.autoselect(Filtered_Img)
        else:
            # autoselection not activated, autoselected image is the filtered image
            Autosel_Img = Filtered_Img

        # print update results
        track_str = f"Image {i}\n" + str(Tracker)
        print(track_str)

        # show camera circle, orthogonal axes, and tracking box
        Marked_Img = markup_img(Autosel_Img, Tracker)

        # show the output frame
        cv2.imshow(gui.win_name, Marked_Img)
        cv2.waitKey(1000)

        # record initial and final images in vlog
        record(logger, [Initial_Img, Filtered_Img], track_str)

    # reset Tracker information (only necessary for multiple iterations of a run
    Tracker.clear()

    # clear window to end simulation
    cv2.destroyWindow(Window)

##############################################################################
#   Possible test runs:
#       + PHD2 Simulation Images: "test1", "test5", "test10"
#       + USB Camera Images: "alnilam", "lamp", "mirphak", "rigel"
if __name__ == "__main__":

    Test = "alnilam"
    Logger = setup_logger()

    # Guiding of single image from a specified folder
    single_run(Test, 1, Logger, lower_thresh=5)

    # Guiding with a folder of 10 images
    #multiple_run(Test, Logger, lower_thresh=10)

# how about now