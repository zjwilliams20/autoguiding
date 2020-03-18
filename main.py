##############################################################################
#                                   autoguiding.py                           #
##############################################################################

import tkinter as tk
from centroidtracker import CentroidTracker
from controller import Controller
from camera import Camera
import gui

##############################################################################
#   Possible test runs:
#       + PHD2 Simulation Images: "test1", "test5", "test10"
#       + USB Camera Images: "alnilam", "lamp", "mirphak", "rigel"
if __name__ == "__main__":

    root = tk.Tk()
    root.title('Autoguiding Program')

    ct = CentroidTracker()
    con = Controller()
    cam = Camera()

    App = gui.MainApp(root, ct, con, cam)
    App.update()

    root.mainloop()
