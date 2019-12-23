# Autoguiding Program
![Astrothots Logo](/astrothots.PNG)
### Project Background
The Astrophotography Camera is a four-person project that is intended to start with an existing telescope and mount without motors. The four subsystems include:
1. CMOS Imager - build the CMOS camera for imaging including a sensor, peltier cooling junction, and the FPGA to route sensor data.
1. Image Processing - take the bits from the FPGA to form image files, apply filters to remove noise and add color, and apply image stacking to create one final image.
1. Mount automation - equip the mount with motors connected to an MCU for the RA and Dec axes.
1. Autoguiding - attach a USB Camera to the finder scope and figure out where to move the motors based on the generated images.
### Program Summary
The autoguiding program is designed to take a sequence of image captures from a USB Camera as input. From the images taken from the camera, the program takes the following steps to generate motor rates:
1. **Load Image** - either from USB Camera capture or simulation directory
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
    1. transmit rates for RA and Dec periodically
### Validation Plan
**Tasks:**
* attach a USB Camera to the finder scope
* take multiple pictures of the sky to simulate a live capture
* interface the USB Camera to the autoguiding program on the host PC
* apply guiding algorithms to output motor instructions

**Additional Accomplishments:**
* four test simulations created containing 10 images each
* primitive gui for user to watch live progress of autoguiding
* visual-logging file to see each image in the sequence
* autoselection algorithm to find a star from the center
* CentroidTracker class to keep track of all stars in the image
    
![Orion Galaxy](https://astrobrunomarshall.files.wordpress.com/2012/06/02-orion-nebula.jpg)
