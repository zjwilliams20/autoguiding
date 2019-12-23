<h1>Autoguiding Program</h1>
____________________________________________________________________

Author: Zach Williams
Date:   18 Nov, 2019
Team:   Astrophotography Camera

____________________________________________________________________

Project Background:
The Astrophotography Camera is a four-person project that is
intended to start with an existing telescope and mount without motors.
The four subsystems include:
    1. CMOS Imager - build the CMOS camera for imaging including a
    sensor, peltier cooling junction, and the FPGA to route sensor data.
    2. Image Processing - take the bits from the FPGA to form image
    files, apply filters to remove noise and add color, and apply
    image stacking to create one final image.
    3. Mount automation - equip the mount with motors connected to
    an MCU for the RA and Dec axes.
  **4. Autoguiding - attach a USB Camera to the finder scope and figure
    out where to move the motors based on the generated images.
** - this is where the current program resides.

Summary:
The autoguiding program is designed to take a sequence of image captures
from a USB Camera as input. From the images taken from the camera, the
program takes the following steps to generate motor rates:
    1. Load Image - either from USB Camera capture or simulation directory
    2. Image Processing:
        + crop image to get relevant camera view
        + maximize image for best pixel flexibility
        + apply filters: RGB to grayscale and binary threshold
        + use findContours() to locate centroids of stars in view
    3. Centroid Tracking:
        + input the newly found centroids
        + compare to the current centroids to get final list
        + autoselect a star if not currently tracking
        + get displacement from center if currently tracking
    4. PI Controller:
        + input the displacement from the center of the frame
        + output the rates for the RA and Dec axes respectively
    5. USB Connection:
        + transmit rates for RA and Dec periodically