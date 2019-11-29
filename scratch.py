##############################################################################
#                               scratch.py                                 #
##############################################################################

import centroidtracker as ct
import cv2
import gui

tcker = ct.CentroidTracker()
gui = gui.win_name
test = cv2.imread("test.png")
test = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
test = cv2.cvtColor(test, cv2.COLOR_GRAY2BGR)

crop = test[90:395, 165:470]
(cX, cY) = (270, 265)

resized = cv2.resize(crop, None, fx=1.75, fy=1.75,
                   interpolation=cv2.INTER_LINEAR_EXACT)

size = resized.shape
print(f"cx:{size[0]/2}\tcy:{size[1]/2}")
axes = cv2.line(resized, (cX, 0), (cX, resized.shape[1]),
                      color=(0,0,200), thickness=1, lineType=cv2.LINE_4)
axes = cv2.line(axes, (0, cY), (resized.shape[0], cY),
                      color=(0, 0, 200), thickness=1, lineType=cv2.LINE_4)
circle = cv2.circle(axes, (cX, cY), radius=cY, color=(0,0,200))

cv2.imshow(gui, axes)
cv2.waitKey(-1)

# from astropy import units as u
# from astropy.coordinates import SkyCoord
# from astropy.table import QTable
# from matplotlib import pyplot as plt
#
# t = QTable.read('data/rosat.vot', format='votable')
#
# eq = SkyCoord(t['RAJ2000'], t['DEJ2000'])
# gal = eq.galactic
#
# fig = plt.figure()
# ax = fig.add_subplot(1,1,1, aspect='equal')
# ax.scatter(gal.l, gal.b, s=1, color='black')
# ax.set_xlim(0., 360.)
# ax.set_ylim(-90., 90.)
# ax.set_xlabel("Galactic Longitude")
# ax.set_ylabel("Galactic Latitude")
#
# fig.savefig('coord_level2.png', bbox_inches='tight')