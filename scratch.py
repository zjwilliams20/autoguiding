##############################################################################
#                               scratch.py                                 #
##############################################################################

import calibration as cal

def calibration(app):

    # Calibration Logic
    ###########################################
    # start exposing and tracking
    # transmit calRates
    # get COM
    # transmit calRates
    # get COM
    # ...
    # 10th COM loaded
    # transmit negCalRates to return to center
    # repeat for motor 2
    # calculate conversion matrix

    # Normal Operation
    ###########################################
    # start exposing & tracking
    # get COM
    # plug into conversion matrix
    # plug into PI controller
    # transmit guideRates to MCU
    # repeat

    calDecRate = 5
    calRARate = 5
    app.UART.transmit(calDecRate, calRARate)

if __name__ == "__main__":

    pass
