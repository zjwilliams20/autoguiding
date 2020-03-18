##############################################################################
#                              controller.py                                 #
##############################################################################

##############################################################################
class Controller:
    """A Proportional Integral Controller that provides motor instructions
    to the mount subsystem. Fields have also been made to add a derivative
    part to the controller, but this isn't currently implemented."""

    ####################################################################
    def __init__(self):
        """Create basic PI Controller."""

        # Controller constants --> still need tuning with actual mount
        # Motor X
        self.RAPropGain = 0.001
        self.RAIntGain = 0.001
        self.RADerivGain = 1
        self.RAErrSum = 0
        self.RAErr = 0

        # Motor Y
        self.DECPropGain = 0.001
        self.DECIntGain = 0.001
        self.DECDerivGain = 1
        self.DECErrSum = 0
        self.DECErr = 0

        self.scale = 1000
        self.integralThreshold = 0.3

    ####################################################################
    def calculate(self, dX, dY):
        """Output a motor rate correction based on an input displacement.
        If the integral term gets too big due to error accumulation, clamp
        it to a specified value."""

        # Set cumulitive sums from input error
        self.RAErrSum += dX
        self.DECErrSum += dY

        # set current error terms
        self.RAErr = dX
        self.DECErr = dY

        # set RA motor derivative and integral components
        RADerTerm = self.RAPropGain * dX
        RAIntTerm = self.RAIntGain * self.RAErrSum

        # set DEC motor derivative and integral components
        DECDerTerm = self.DECPropGain * dY
        DECIntTerm = self.DECIntGain * self.DECErrSum

        # if either integral term goes above threshold due to error accumulation, clamp to 0.3
        if RAIntTerm / self.scale > self.intThresh:
            RAIntTerm = 0.3

        if DECIntTerm / self.scale > self.intThresh:
            DECIntTerm = 0.3

        # calculate the acutal rates by the rounded and scaled sum of each term
        RARate = round((RADerTerm + RAIntTerm) / self.scale, 3)
        DECRate = round((DECDerTerm + DECIntTerm) / self.scale, 3)

        return RARate, DECRate
