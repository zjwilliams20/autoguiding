##############################################################################
#                              camera.py                                     #
##############################################################################

import cv2

##############################################################################
class Camera:

    ####################################################################
    def __init__(self, captureRate=1000):
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cam.isOpened():
            print("ERR: Cannot open camera")
            exit()
        self.captureRate = captureRate
        print("Prepping camera...")
        cv2.waitKey(1000)

    ####################################################################
    def capture(self):
        # Capture frame-by-frame
        ret, img = self.cam.read()
        # if frame is read correctly ret is True
        if not ret:
            print("ERR: Frame not received")

        cv2.imwrite("test.png", img)
        #cv2.imshow("Imaging Workbench", img)
        cv2.waitKey(self.captureRate - 500)
        return img
