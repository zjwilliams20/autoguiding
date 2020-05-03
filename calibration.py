##############################################################################
#                             calibration.py                                 #
##############################################################################

import numpy as np
import matplotlib.pyplot as plt
import math

##############################################################################
class Calibration:

    # State constants
    IDLE     = 0
    BUF_0    = 1
    RA_OUT   = 2
    BUF_1    = 3
    RA_IN    = 4
    BUF_2    = 5
    DEC_OUT  = 6
    BUF_3    = 7
    DEC_IN   = 8
    DONE     = 9

    # State timing
    SHORT_WAIT = 1
    LONG_WAIT =  1

    ####################################################################
    def __init__(self):

        # convert from pixel error to motor error
        self.conversion = np.array(([0, 0], [0, 0]))

        # number of samples for each motor
        self.nSamples = 10

        # motor data points, where data points are (x_i, y_i, sigma_i)
        # and sigma_i is the amplitude of the motor rate
        self.RAmotor = np.zeros((self.nSamples, 3))
        self.DECmotor = np.zeros((self.nSamples, 3))

        # Calibration rates for each motor
        self.RACalRate = 0.3
        self.DECCalRate = 0.1

        # Current rate for each motor
        self.RARate = 0
        self.DECRate = 0

        # Current sample number
        self.index = 0

        # Where are we in the calibration
        self.state = self.IDLE

    ####################################################################
    def __str__(self):
        return f"\nConversion Matrix: \n{self.conversion}"   \
               f"\nRA Motor Sample Points:\n{self.RAmotor}"   \
               f"\nDEC Motor Sample Points:\n{self.DECmotor}"

    ####################################################################
    def add_data_point(self, COM, sigma, motor):
        """Add an (x, y) tuple to the specified motor's calibration data."""
        if motor is 'RA':
            self.RAmotor[self.index] = (COM[0], COM[1], sigma)
        elif motor is 'DEC':
            self.DECmotor[self.index] = (COM[0], COM[1], sigma)

    ####################################################################
    def set_rates(self, RARate, DECRate):
        self.RARate = RARate
        self.DECRate = DECRate

    ####################################################################
    def calculate_rates(self, COM):
        """Map pixel rates to motor rates with conversion matrix"""
        return np.dot(self.conversion, COM)

    ####################################################################
    def execute(self, UART, status):
        """Set the output rates based on the current state. Add a data point to the sample """

        # don't move in idle, buffer states, or done
        if self.state is self.IDLE\
            or self.state is self.BUF_0\
            or self.state is self.BUF_1\
            or self.state is self.BUF_2\
            or self.state is self.BUF_3\
            or self.state is self.DONE:
                self.set_rates(0, 0)

        # rotator calibration rate for RA motor
        elif self.state is self.RA_OUT:
            self.set_rates(self.RACalRate, 0)
            self.add_data_point(status.COM, self.RARate, 'RA')

        # negative rotator calibration rate for RA motor
        elif self.state is self.RA_IN:
            self.set_rates(-1 * self.RACalRate, 0)

        # declination calibration rate for DEC motor
        elif self.state is self.DEC_OUT:
            self.set_rates(0, self.DECCalRate)
            self.add_data_point(status.COM, self.DECRate, 'DEC')

        # negative declination calibration rate for DEC motor
        elif self.state is self.DEC_IN:
            self.set_rates(0, -1 * self.DECCalRate)

        # transmit rates to microcontroller
        UART.transmit(self.RARate, self.DECRate)

        # increment state index
        self.index = self.index + 1

    ####################################################################
    def next_state(self):
        """Next state logic that keeps track of where we are in the calibration."""

        # called upon first call to calibrate()
        if self.state is self.IDLE:
            self.state = self.BUF_0
            self.index = 0
            print("\t<IDLE>")

        # wait for 3 updates
        elif self.state is self.BUF_0 and self.index is self.SHORT_WAIT:
            self.state = self.RA_OUT
            self.index = 0
            print("\t<RA_OUT>")

        # take nSamples for RA motor
        elif self.state is self.RA_OUT and self.index is self.nSamples:
            self.state = self.BUF_1
            self.index = 0
            print("\t<IDLE>")

        # wait for 3 updates
        elif self.state is self.BUF_1 and self.index is self.SHORT_WAIT:
            self.state = self.RA_IN
            self.index = -1 * self.nSamples
            print("\t<RA_IN>")

        # move back to origin for nSamples updates
        elif self.state is self.RA_IN and self.index is 0:
            self.state = self.BUF_2
            self.index = 0 # unneeded

        # wait for 5 updates (***User must center guide star on origin during this period)
        elif self.state is self.BUF_2 and self.index is self.LONG_WAIT:
            self.state = self.DEC_OUT
            self.index = 0
            print("\t<DEC_OUT>")

        # take nSamples samples for DEC Motor
        elif self.state is self.DEC_OUT and self.index is self.nSamples:
            self.state = self.BUF_3
            self.index = 0

        # wait for 3 updates
        elif self.state is self.BUF_3 and self.index is self.SHORT_WAIT:
            self.state = self.DEC_IN
            self.index = -1 * self.nSamples
            print("\t<DEC_IN>")

        # move back to origin for 10 updates
        elif self.state is self.DEC_IN and self.index is 0:
            self.state = self.DONE
            self.index = 0
            print("\t<DONE>")

    ####################################################################
    def least_squares(self):

        # Get test data from calibration instance
        RASamples = self.RAmotor.shape[0]
        DECSamples = self.DECmotor.shape[0]

        # Warn user if number of samples doesn't match
        if RASamples is not DECSamples:
            print("<WARNING: # RASamples doesn't equal DECSamples")

        aNum = np.zeros(RASamples)
        bNum = np.zeros(RASamples)
        sigArr = np.zeros(RASamples)

        print(self.RAmotor)
        print(self.DECmotor)

        # Compute least squares to get a, b, c, and d constants
        for i in range(RASamples):
            aNum[i] = self.RAmotor[i][0] * self.RAmotor[i][2]
            bNum[i] = self.RAmotor[i][1] * self.RAmotor[i][2]
            sigArr[i] = self.RAmotor[i][2] ** 2
        a, b = sum(aNum) / sum(sigArr), sum(bNum) / sum(sigArr)

        for i in range(DECSamples):
            aNum[i] = self.DECmotor[i][0] * self.DECmotor[i][2]
            bNum[i] = self.DECmotor[i][1] * self.DECmotor[i][2]
            sigArr[i] = self.DECmotor[i][2] ** 2
        c, d = sum(aNum) / sum(sigArr), sum(bNum) / sum(sigArr)

        # create a numpy array
        array = np.array(([a, b], [c, d]))

        # Find conversion matrix with SVD
        u, s, vh = np.linalg.svd(array, full_matrices=True)
        self.conversion = np.dot(u * s, vh)

        # negate y-axis for consistency
        self.conversion = self.conversion * np.array(([-1, -1], [-1, -1]))

####################################################################
def plot_calibration(ThetaData, PhiData, declination, tests):

    # plot Calibration Data
    fig, (ax0, ax1) = plt.subplots(ncols=2, figsize=(20, 10))
    ax0.plot(PhiData[:, 0], PhiData[:, 1], 'rx')
    ax0.plot(ThetaData[:, 0], ThetaData[:, 1], 'bx')

    # aesthetics
    fig.suptitle("Calibration Mathematical Validation", fontsize=16)
    ax0.set_title(f"Calibration Data Acquisition: {declination}\u00B0 Declination")
    ax0.legend(["\u03D5 Motor Points", "\u03B8 Motor Points", "Test Conversion Points"], loc='upper right')
    ax0.set_ylabel("Y-Pixel Displacement")
    ax0.set_xlabel("X-Pixel Displacement")
    ax0.grid()
    ax0.axhline(color='black')
    ax0.axvline(color='black')

    # generate min and max bounds by farthest point
    thresh = 5
    (p1x, p1y), (p2x, p2y) = ThetaData[-1][:2], PhiData[-1][:2]
    xMin = min(p1x, p2x, 0)
    xMax = max(p1x, p2x, 0)
    yMin = min(p1y, p2y, 0)
    yMax = max(p1y, p2y, 0)
    ax0.set_xlim((xMin - thresh, xMax + thresh))
    ax0.set_ylim((yMin - thresh, yMax + thresh))

    # plot Example Test Points
    for i in range(0, len(tests)):
        ax1.plot(tests[i][0][0], tests[i][0][1], 'g*')
        if tests[i][0][1] < 0:
            yOffset = -8
        else:
            yOffset = 3
        ax1.text(tests[i][0][0]-5, tests[i][0][1]+yOffset,
                 f"({int(round(tests[i][0][0], 0))}, {int(round(tests[i][0][1], 0))})"
                 f"\n[{int(round(tests[i][1][1], 0))}, {int(round(tests[i][1][0], 0))}]")
        ax1.annotate('', xy=(0, 0),
                     xytext=(tests[i][0][0], tests[i][0][1]),
                     arrowprops=dict(arrowstyle="->"))
    ax1.legend(["Pixel Coordinates: (x, y)\nMotor Instructions: [\u03B8, \u03D5]"])

    # Aesthetics
    ax1.set_title("Example Converted Test Points")
    ax1.set_ylabel("Y-Pixel Displacement")
    ax1.set_xlabel("X-Pixel Displacement")
    ax1.grid()
    ax1.axhline(color='black')
    ax1.axvline(color='black')
    ax1.set_ylim((-80, 80))
    ax1.set_xlim((-80, 80))

def calibration_simulation(dec, rot):
    """Conduct an isolated calibration simulation to verify math checks out."""

    # Create calibration instance
    test = Calibration()

    # Create Data
    dataMotor = np.array(range(0, 100, 10))
    dataSigma = 10 * np.ones(10)

    PhiData =  [math.cos(math.radians(dec + rot)) * dataMotor, math.sin(math.radians(dec + rot)) * dataMotor, dataSigma]
    ThetaData = [math.cos(math.radians(rot)) * dataMotor, math.sin(math.radians(rot)) * dataMotor, dataSigma]

    test.DECmotor = np.transpose(np.array(ThetaData))
    test.RAmotor = np.transpose(np.array(PhiData))

    # Use least squares to get conversion matrix
    test.least_squares()

    # Make 2 differently sized circles with three points each
    COMs = []
    testTheta1 = np.linspace((1/4) * math.pi, (9/4) * math.pi, num=4)
    testTheta2 = np.linspace((3/4) * math.pi, (11/4) * math.pi, num=4)
    for i in range(0, 3):
        COMs.append((30 * math.cos(testTheta1[i]), 30 * math.sin(testTheta1[i])))
        COMs.append((60 * math.cos(testTheta2[i]), 60 * math.sin(testTheta2[i])))

    tests = []
    for i in range(0, len(COMs)):
        tests.append([COMs[i], np.dot(test.conversion, COMs[i])])
    plot_calibration(np.transpose(ThetaData), np.transpose(PhiData), dec, tests)

if __name__ == "__main__":

    # run calibraiton simulation at specified angle and rotation
    calibration_simulation(45, 180)
