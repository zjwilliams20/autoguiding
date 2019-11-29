##############################################################################
#                              controller.py                                 #
##############################################################################

class Controller:
    """A Proportional Integral Controller that provides motor instructions
    to the mount subsystem. Fields have also been made to add a derivative
    part to the controller, but this isn't currently implemented."""

    def __init__(self):
        self.xPropGain = 0.01
        self.xIntGain = 0.0001
        self.xDerivGain = 1
        self.xErrSum = 0
        self.xErr = 0

        self.yPropGain = 0.01
        self.yIntGain = 0.0001
        self.yDerivGain = 1
        self.yErrSum = 0
        self.yErr = 0

    def calculate(self, dX, dY):
        """Output a motor rate correction based on an input displacement."""

        self.xErrSum += dX
        self.yErrSum += dY
        self.xErr = dX
        self.yErr = dY

        xRate = round(self.xPropGain * dX + self.xIntGain * self.xErrSum, 5)
        yRate = round(self.yPropGain * dY + self.yIntGain * self.yErrSum, 5)

        return xRate, yRate

def connect():
    """Connect the autoguiding program to MCU over USB; transmit default
    rate of RA to initiate autoguiding program."""

def transmit():
    """Send a motor rate to the MCU over USB."""

# Graphic for advancement RA/Dec mapped onto the orthogonal axes
#
#                ^  +y = +Dec
#                |
#                |
#   -x = -RA     |      +x = +RA
#     <----------+---------->
#                |
#                |
#                |
#                v   -y = -Dec