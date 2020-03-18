##############################################################################
#                                  gui.py                                    #
##############################################################################

from tkinter import *
from imageprocessing import *
from centroidtracker import CentroidTracker
from calibration import Calibration
from controller import Controller
from status import Status

# Tkinter GUI application
##############################################################################
class MainApp:

    ####################################################################
    def __init__(self, master, camera, uart):
        """Create a main application with the root thread, camera, and
        UART instances."""

        # Member Data
        #######################################################
        self.tracker = CentroidTracker()
        self.controller = Controller()
        self.test = "alnilam"
        self.status = Status()
        self.threshold = 5
        self.camera = camera
        self.UART = uart

        # GUI Status Data
        #######################################################
        self.exposing = False
        self.calibrating = False
        self.calibrated = False
        self.running = False

        # Calibration Data
        #######################################################
        self.calibration = Calibration()

        # Primary GUI Objects
        #######################################################
        # master root frame
        self.master = master

        # self.img - cv2 binary image without any markup
        # self.gui_img - PIL colored image with markup
        self.img, self.gui_img = initial_img_load(self.tracker)

        # Holds image frame
        self.panel = Label(master, image=self.gui_img)
        self.panel.pack(side=LEFT)

        # Contains all control and output widgets right of image panel
        self.frame = Frame(master)
        self.frame.pack(side=RIGHT, expand=TRUE, fill=BOTH)

        # data that contains calibration and guiding status data
        self.status_txt = StringVar()
        self.status_txt.set(self.tracker.status)

        # GUI object containing status data
        self.text = Label(self.frame, textvariable=self.status_txt)
        self.text.config(height=10, width=32, justify="left", bg="grey25", fg="white")
        self.text.pack()

        # Secondary GUI Objects (widgets)
        #######################################################
        # Binary threshold slider
        self.slider = Scale(self.frame, from_=0, to=200, orient=HORIZONTAL, length=225)
        self.slider.config(sliderlength=15, label="Binary Threshold", bg="grey25", fg="white")
        self.slider.set(5)
        self.slider.pack()

        # Loop button
        self.expose_img = PhotoImage(file="figures/expose.png")
        self.expose_btn = Button(self.frame, image=self.expose_img, command=self.expose_button_cb)
        self.expose_btn.config(height=20, width=20, bg="white")
        self.expose_btn.pack(side="left", anchor=NW)
        self.expose_ttp = CreateToolTip(self.expose_btn, "Begin looping exposures from tracking camera")

        # Run button
        self.run_img = PhotoImage(file="figures/run_gs.png")
        self.run_btn = Button(self.frame, image=self.run_img, command=self.run_button_cb)
        self.run_btn.config(height=20, width=20, bg="white")
        self.run_btn.pack(side="left", anchor=NW)
        self.run_ttp = CreateToolTip(self.run_btn, "Start autoguiding program")

        # Stop button
        self.stop_img = PhotoImage(file="figures/stop_gs.png")
        self.stop_btn = Button(self.frame, image=self.stop_img, command=self.stop_button_cb)
        self.stop_btn.config(height=20, width=20, bg="white")
        self.stop_btn.pack(side="left", anchor=NW)
        self.stop_ttp = CreateToolTip(self.stop_btn, "Stop looping and guiding")

        # Calibration button
        self.cal_img = PhotoImage(file="figures/cal_gs.png")
        self.cal_btn = Button(self.frame, image=self.cal_img, command=self.cal_button_cb)
        self.cal_btn.config(height=20, width=20, bg="white")
        self.cal_btn.pack(side="left", anchor=NW)
        self.cal_ttp = CreateToolTip(self.cal_btn, "Begin calibration sequence")

    ####################################################################
    def update(self):
        """Implement the desired appropriate function and update the GUI
         objects depending on the desired outcome. Repeat every second
         (1000 ms).

        Possible configurations:
            1) idle
            2) exposing
            3) exposing and calibrating
            4) exposing and running
        """

        # Take camera captures and find guide star if exposing
        if self.exposing:
            self.expose()

            # Calibrate motors
            if self.calibrating:
                self.calibrate()

            # Or Implement guiding algorithm with transmission of motor rates
            elif self.running:
                self.run()

            # Reset img_num if it reaches 10 --> temporary
            if self.tracker.status.img_num is 10:
                self.tracker.status.clear()
                # self.tracker.clear()

            # Update panel image, threshold slider, and status text after exposure and run
            self.panel.config(image=self.gui_img)
            self.threshold = self.slider.get()
            self.status_txt.set(self.tracker.status)

        # Don't do anything if not exposing
        elif not self.exposing:
            pass

        # Update color of calibration button given tracking status
        # can't calibrate if currently calibrating or already calibrated
        if self.calibrated or self.calibrating:
            self.cal_img = PhotoImage(file="figures/cal_gs.png")
        else:
            # can calibrate if our tracker is LOCKED
            if self.tracker.status.mode is self.tracker.LOCKED:
                self.cal_img = PhotoImage(file="figures/cal.png")
            # don't calibrate if looking for a guide star
            else:
                self.cal_img = PhotoImage(file="figures/cal_gs.png")
        self.cal_btn.config(image=self.cal_img)

        # Rerun update every second
        self.master.after(1000, self.update)

    ####################################################################
    def expose(self):
        """Load an image either from a test directory or the actual USB
        Camera, and autoselect the guide star closest to the center."""

        # Either A) load image from test directory
        self.img = load_image(self.test, self.tracker.status.img_num)
        # or B) capture frame from USB Camera
        # initial_img = self.camera.capture()

        # locate the centroids as a list of (x, y) tuples and get binary thresholded image
        centroids, colored_img  = find_centroids(self.img, lower_thresh=self.threshold)

        # update the Tracker object for the next list of input centroids
        dX, dY = self.tracker.update(centroids)

        # if the mode is SEARCHING, autoselect a guide star
        if self.tracker.status.mode is self.tracker.SEARCHING:
            # get a guide star and return image with smallest bounding rectangle
            autosel_img = self.tracker.autoselect(colored_img)
        else:
            # autoselection not activated, autoselected image is the filtered image
            autosel_img = colored_img

        # show camera circle, orthogonal axes, and tracking box
        marked_img = markup_img(autosel_img, self.tracker)
        pil_img = Image.fromarray(marked_img)
        self.gui_img = ImageTk.PhotoImage(pil_img)

        # Update status object incremented image number, mode, and displacement
        self.tracker.status.set(self.tracker.status.img_num + 1, self.tracker.status.mode, (dX, dY))

    ####################################################################
    def run(self):
        """Run the autoguiding program.

        More specifically, plug in pixel error into the conversion matrix
        to get motor error, plug into the controller, and transmit the final
        motor rates to the MCU. Note: this is only accessible after a
        successful calibration."""

        # Fetch distance from origin
        dX, dY = self.tracker.status.COM

        # Plug into conversion matrix
        calRARate, calDECRate = self.calibration.calculate_rates((dX, dY))

        # Get rates from PI Controller
        raRate, decRate = self.controller.calculate(calRARate, calDECRate)

        # Transmit calculated motor rates over UART
        self.UART.transmit(raRate, decRate)

        # Update status object motor rates
        self.tracker.status.set_rates(raRate, decRate)

    ####################################################################
    def calibrate(self):
        """Calibrate the program. More specifically, individually move each
         motor to get sample points along each axis, and calculate a conversion
         matrix that will map (x, y) pixel error into error along each motor axis.

         This is necessary because at different declinations, orthogonal pixel
         error doesn't directly correspond to motor error. Adjustments to the
         rotator angle will correspond to different angles relative to the
         camera frame."""

        # tell motors what to do and record data samples if necessary
        self.calibration.execute(self.UART, self.tracker.status)

        # next state logic based on calibration state
        self.calibration.next_state()

        # update status object for current calibration rates
        self.tracker.status.set_rates(self.calibration.RARate, self.calibration.DECRate)

        # After calibration finishes...
        if self.calibration.state is self.calibration.DONE:
            self.calibration.least_squares()    # run least squares to get conversion matrix
            self.calibrating = False            # stop calibrating
            self.calibrated = True              # calibration has finished
            self.stop_button_cb()               # stop all processes
            print(self.calibration)             # print result

    # GUI Operational state codes
    ####################################################################
    # CI - calibrating
    # CD - calibrated
    # E  - exposing
    # R  - running
    # S  - stop

    ####################################################################
    def expose_button_cb(self):
        if self.exposing:
            print("<E: no action>")
        elif not self.exposing:
            print("<!E: start exposing>")
            self.exposing = True

            # if calibrated, user can now run
            if self.calibrated:
                self.run_img = PhotoImage(file="figures/run.png")
                self.cal_img = PhotoImage(file="figures/cal_gs.png")

            # user can't run if not calibrated
            elif not self.calibrated:
                self.run_img = PhotoImage(file="figures/run_gs.png")

            # can't expose if we're already exposing
            self.expose_img = PhotoImage(file="figures/expose_gs.png")
            self.stop_img = PhotoImage(file="figures/stop.png")

            # update GUI object colors
            self.run_btn.config(image=self.run_img)
            self.expose_btn.config(image=self.expose_img)
            self.stop_btn.config(image=self.stop_img)
            self.cal_btn.config(image=self.cal_img)

    ####################################################################
    def stop_button_cb(self):
        self.exposing = False
        self.running = False

        # Warn user about incomplete calibration
        if self.calibrating:
            print("<WARNING: !CD>")
            self.calibrating = False
            self.calibrated = False

        # can't do anything until we expose again
        self.expose_img = PhotoImage(file="figures/expose.png")
        self.run_img = PhotoImage(file="figures/run_gs.png")
        self.stop_img = PhotoImage(file="figures/stop_gs.png")
        self.cal_img = PhotoImage(file="figures/cal_gs.png")

        # update GUI object colors
        self.expose_btn.config(image=self.expose_img)
        self.run_btn.config(image=self.run_img)
        self.stop_btn.config(image=self.stop_img)
        self.cal_btn.config(image=self.cal_img)
        print("<S: stop all>")

    ####################################################################
    def run_button_cb(self):
        # Only run if currently exposing and calibration done
        if self.exposing and self.calibrated:
            if self.running:
                print("<R; no action>")
            elif not self.running:
                self.run_img = PhotoImage(file="figures/run_gs.png")
                self.running = True
                print("<CD, E, and !R; set R>")
            self.run_btn.config(image=self.run_img)

        # Do nothing if not currently running
        elif not self.exposing:
            print("<!E; no action>")
        elif not self.calibrated:
            print("<!CD; no action>")

    ####################################################################
    def cal_button_cb(self):
        # only calibrate if we haven't already done so
        if not self.calibrated:
            if not self.calibrating:
                if self.exposing and self.tracker.status.mode is self.tracker.LOCKED:
                    print("<!CD, !CI, E, and LOCKED; start calibrating>")
                    self.cal_img = PhotoImage(file="figures/cal_gs.png")
                    self.calibrating = True
                    self.cal_btn.config(image=self.cal_img)
                elif not self.exposing:
                    print("<!CD but !E; no action>")
                elif self.tracker.status.mode is not self.tracker.LOCKED:
                    print("<!LOCKED; can't calibrate>")

            # accept calibration while exposing
            elif self.calibrating:
                print("<CI; no action>")


        # don't do anything if already calibrated
        else:
            print("<CD: do nothing>")


##############################################################################
class CreateToolTip(object):
    """
    Create a tooltip for a given widget.
    Adapted from @Stevoisiak on stackoverflow.com
    https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    """
    ####################################################################
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    ####################################################################
    def enter(self, event=None):
        self.schedule()

    ####################################################################
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    ####################################################################
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    ####################################################################
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    ####################################################################
    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    ####################################################################
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()