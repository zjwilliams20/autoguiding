##############################################################################
#                              camera.py                                     #
##############################################################################

import cv2
import time

##############################################################################
class Camera:

    ####################################################################
    def __init__(self, captureRate=1000):
        """Open the USB Camera, exit on error."""

        try:
            self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        except:
            exit("\t<ERROR: check USB Camera connection>")

        if not self.cam.isOpened():
            exit("\t<ERROR: Unable to open USB Camera>")

        self.captureRate = captureRate
        time.sleep(1)
        print("<camera ready>")

    ####################################################################
    def capture(self):
        """Grab a single frame from the camera, return the cv2 image."""

        # Capture frame-by-frame
        ret, img = self.cam.read()

        # print during frame errors
        if not ret:
            print("\t<ERR: Frame not received>")

        # allow small amount of buffer time
        time.sleep(self.captureRate / 1000)

        return img

    ##############################################################################
    def get_samples(self, count):
        """"Get a specified number of images to be stored in the current directory.
        Used to generate test images for development purposes."""

        print("Beginning sample capture...")
        for i in range(count):
            print(f"\tSample {i}")
            img = self.capture()
            img_name =  f"sample.png"
            cv2.waitKey(500)    # time.sleep(0.5)
            cv2.imwrite(img_name, img)

