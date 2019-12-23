# Autoguiding Program
![Orion Galaxy](/orion.jpg)

### Project Background
The Astrophotography Camera is a four-person project that is intended to start with an existing telescope and mount without motors. The four subsystems include:
1. CMOS Imager - build the CMOS camera for imaging including a sensor, peltier cooling junction, and the FPGA to route sensor data.
1. Image Processing - take the bits from the FPGA to form image files, apply filters to remove noise and add color, and apply image stacking to create one final image.
1. Mount automation - equip the mount with motors connected to an MCU for the RA and Dec axes.
1. ++Autoguiding - attach a USB Camera to the finder scope and figure out where to move the motors based on the generated images.

++ - this is where the current program resides.

### Summary
The autoguiding program is designed to take a sequence of image captures from a USB Camera as input. From the images taken from the camera, the program takes the following steps to generate motor rates:
1. Load Image - either from USB Camera capture or simulation directory
1. Image Processing:
    1. crop image to get relevant camera view
    1. maximize image for best pixel flexibility
    1. apply filters: RGB to grayscale and binary threshold
    1. use findContours() to locate centroids of stars in view
1. Centroid Tracking:
    1. input the newly found centroids
    1. compare to the current centroids to get final list
    1. autoselect a star if not currently tracking
    1. get displacement from center if currently tracking
1. PI Controller:
    1. input the displacement from the center of the frame
    1. output the rates for the RA and Dec axes respectively
1. USB Connection:
    1. transmit rates for RA and Dec periodically
