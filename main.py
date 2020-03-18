##############################################################################
#                                   main.py                                  #
##############################################################################

import tkinter as tk
from camera import Camera
from uart import UART
import gui

##############################################################################
if __name__ == "__main__":

    # create Tk root widget
    root = tk.Tk()
    root.title('Autoguiding Program')

    # open the two devices, quit if either isn't connected
    cam = Camera()
    uart = UART()

    # start the main application
    App = gui.MainApp(root, cam, uart)
    App.update()

    root.mainloop()

# can you hear me?