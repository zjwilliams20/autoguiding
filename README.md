# Autoguiding Program
![Astrothots Logo](/figures/astrothots.PNG)
### Project Background
The Astrophotography Camera is a four-person project. Its five subsystems include:
1. Imager PCB - responsible for imaging including a CMOS sensor, peltier cooling junction, and signals to route the data to the Carrier Card
1. FPGA Carrier Card - PCB that interfaces with the FPGA's signals, including Ethernet, SD Card, and ribbon cables from the CMOS sensor.
1. Image Processing - takes the bits from the FPGA to form image files, apply filters to remove noise and add color, and apply image stacking to create one final image.
1. Mount automation - equip the mount with motors connected to an MCU for the RA and Dec axes.
1. Autoguiding - attach a USB Camera to the finder scope and figure out where to move the motors based on the generated images.

### Program Summary
The autoguiding program is designed to take a sequence of image captures from a USB Camera as input. From these images, the program takes the following steps to generate motor rates:
1. **Load Image** - either from USB Camera capture or local simulation directory
2. **Image Processing:**
    1. crop image to get relevant camera view
    1. maximize image for best pixel flexibility
    1. apply filters: RGB to grayscale and binary threshold
    1. use findContours() to locate centroids of stars in view
3. **Centroid Tracking:**
    1. input the newly found centroids
    1. compare to the current centroids to get final list
    1. autoselect a star if not currently tracking
    1. get displacement from center if currently tracking
4. **PI Controller:**
    1. input the displacement from the center of the frame
    1. output the rates for the RA and Dec axes respectively
5. **USB Connection:**
    1. transmit rates for RA and Dec periodically over UART

### Using the Program
Upon entering the program, the user will be expected to have both the USB Camera and the UART-TTL converter connected. If either of these aren't operational, the program will exit. After entering the primary loop, the user can either run with the pictures from the camera, or the sample images provided.

With everything set up, the user can now begin exposing to continuously view the image from the USB Camera, and track the stars in view. Depending on the brightness outside, the user might have to adjust the binary threshold with the slider provided. Before the user can begin sending instructions to the mount, a calibration must be conducted. See the CalibrationMath.pdf for a more detailed explanation of this step. After successfully calibrating, the program will be operational for autoguiding with the controller.

![Orion Galaxy](https://astrobrunomarshall.files.wordpress.com/2012/06/02-orion-nebula.jpg)
