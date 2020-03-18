##############################################################################
#                                  status.py                                 #
##############################################################################

##############################################################################
class Status:
    """Simple container class to store information of a current autoguiding
    state including:
        + image number
        + tracking mode
        + center of mass
        + rotator angle motor rate
        + declination motor rate
    """

    # Statuses from centroidtracker.py
    SEARCHING = 0  # searching for guide star
    LOCKED = 1  # star locked in current frame
    LOST = 2  # not implemented in current state, possible future addition

    ####################################################################
    def __init__(self):
        self.img_num = 0
        self.mode = self.SEARCHING
        self.COM = (0, 0)
        self.raRate = 0
        self.decRate = 0

    ####################################################################
    def __str__(self):
        """Represent the state object as a string for printing to the GUI window."""

        state_str = f"Image {self.img_num}" \
        "\n__________________________________________"

        if self.mode is self.SEARCHING:
            state_str += "\n\tMode:\t\tSEARCHING"
        elif self.mode is self.LOCKED:
            state_str += "\n\tMode:\t\tLOCKED"
        elif self.mode is self.LOST:
            state_str += "\n\tMode:\t\tLOST"

        return state_str + \
            f"\n\tTrack Star COM:\t{self.COM}" \
            f"\n\tRA Rate:\t\t{self.raRate}" \
            f"\n\tDec Rate:\t{self.decRate}"

    ####################################################################
    def set(self, img_num, mode=0, COM=(0, 0), raRate=0, decRate=0):
        """Set the fields of a State object with defaults of 0."""
        self.img_num = img_num
        self.mode = mode
        self.COM = COM
        self.raRate = raRate
        self.decRate = decRate

    ####################################################################
    def set_rates(self, raRate, decRate):
        """Set the rates accordingly."""
        self.raRate = raRate
        self.decRate = decRate

    ####################################################################
    def clear(self):
        """Reset the state to the default."""
        return self.__init__()
