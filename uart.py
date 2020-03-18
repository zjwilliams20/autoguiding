##############################################################################
#                                   uart.py                                  #
##############################################################################

from serial import Serial
from time import sleep

##############################################################################
class UART:

    ####################################################################
    def __init__(self):
        """Open the serial port of the UART-TTL Converter as 'COM3' in Windows.
        Exit if any errors occur."""

        self.port = 'COM3'
        self.baud = 9600

        try:
            self.ser = Serial(self.port, self.baud)
        except:
            exit("<ERROR: check serial connection>")

        if not self.ser.is_open:
            exit(f"<ERROR: can't open serial port: {self.port}>")

        self.connect()

    ####################################################################
    def connect(self):
        """Connect the autoguiding program to MCU by echoing a message;
        (Not currently implemented, because stable connection is assumed
        after opening the port)."""

        wBytes = self.ser.write(str('UART Enabled').encode('ascii'))
        sleep(0.05)
        echoStr = self.ser.read(self.ser.in_waiting)
        if echoStr is 'UART Enabled':
            print(f'\t<Connection Succesful: {echoStr}>\n')

    ####################################################################
    def transmit(self, raRate, decRate):
        """Send motor rates to the MCU."""

        # send raRate and decRate with 3 digits beyond decimal, add in extra
        # spaces to ensure MCU program catches all characters.
        data = f" {raRate:.3f} {decRate:.3f}  "
        try:
            self.ser.write(data.encode('ascii'))
            sleep(0.1)
            echoStr = self.ser.read(self.ser.in_waiting)
        except:
            exit("<ERROR: check serial connection>")

        print(echoStr.decode('utf-8'))

    ####################################################################
    def disconnect(self):
        """Disconnect UART serial port."""
        self.ser.close()