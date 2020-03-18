##############################################################################
#                             calibration.py                                 #
##############################################################################

import numpy as np

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
        self.nSamples = 2

        # motor data points
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

        # wait for 3 updates
        elif self.state is self.BUF_0 and self.index is self.SHORT_WAIT:
            self.state = self.RA_OUT
            self.index = 0
            print("\t<RA_OUT>")

        # take nSamples for RA motor
        elif self.state is self.RA_OUT and self.index is self.nSamples:
            self.state = self.BUF_1
            self.index = 0

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

        aNum = np.zeros(RASamples); bNum = np.zeros(RASamples)
        sigArr = np.zeros(RASamples)

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

####################################################################
def calibration_simulation():
    """Conduct an isolated calibration simulation to verify math checks out."""

    # Dummy data
    data1 = list(range(0, -100, -10))
    data2 = list(range(0, 100, 10))

    # Create calibration instance
    test = Calibration()

    # Generate calibration simulation data points
    for i in range(10):
        test.add_data((data1[i], 0), 10, 'X')
        test.add_data((0, data2[i]), 10, 'Y')

    # Use least squares to get conversion matrix
    test.least_squares()

    # Test points
    COMx1 = (-50, 0)
    COMx2 = (50, 0)
    COMy1 = (0, -50)
    COMy2 = (0, 50)
    COMtheta = (25, 25)

    print(test.conversion)
    print(f"conv(COMx1) = {np.dot(test.conversion, COMx1)}")
    print(f"conv(COMx2) = {np.dot(test.conversion, COMx2)}")
    print(f"conv(COMy1) = {np.dot(test.conversion, COMy1)}")
    print(f"conv(COMy2) = {np.dot(test.conversion, COMy2)}")
    print(f"conv(COMtheta) = {np.dot(test.conversion, COMtheta)}")

if __name__ == "__main__":
    calibration_simulation()