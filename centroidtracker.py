##############################################################################
#                           centroidtracker.py                               #
##############################################################################

# Adapted from https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
# From Adrian Rosebrock

# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

##############################################################################
class CentroidTracker:
    """Keeps record of currently tracked stars and provides functionality to
    compare current list to an input list of points to generate a final list."""

    # Statuses
    SEARCHING = 0   # searching for guide star using autoselect()
    LOCKED =    1   # star locked in current frame
    LOST =      2   # not implemented in current state, possible future addition
    
    # Origin (Center of image frame)
    (orgX, orgY) = (270, 265)

    ####################################################################
    def __init__(self, maxDisappeared=1):
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.trackStar = {-1:(0,0)}
        self.mode = self.SEARCHING

        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.maxDisappeared = maxDisappeared

    ####################################################################
    def __str__(self):
        # get current trackStar information
        currID, currCoM = self.getTrackStar()

        # center of mass relative to the image origin (orgX, orgY)
        relativeCoM = (currCoM[0] - CentroidTracker.orgX, CentroidTracker.orgY - currCoM[1])
        text = "\t\tstatus: "
        if self.mode is self.LOCKED:
            text += "LOCKED"
            text += f"\n\t\ttrackStar:\tID# {currID} " \
                    f"\n\t\t\t\t\tCoM {relativeCoM}"
        elif self.mode is self.SEARCHING:
            text += "SEARCHING"
        elif self.mode is self.LOST:
            text += "LOST"
        return text

    ####################################################################
    def clear(self):
        """Clear the objects, disappeared, and trackStar to return a
        blank version of the CentroidTracker. (not currently implemented)."""
        return self.__init__()

    ####################################################################
    def getTrackStar(self):
        """Return a tuple comprising the trackStar's ID and center of mass."""
        return list(self.trackStar.items())[0]

    ####################################################################
    def setTrackStar(self, star):
        """Set the new trackStar for the current CentroidTracker."""
        self.trackStar = star

    ####################################################################
    def autoselect(self, img):
        """Choose a centroid as close to the center of the screen as possible
        and update mode to tracking mode."""

        # center of cropped USB Camera image
        (orgX, orgY) = (CentroidTracker.orgX, CentroidTracker.orgY)
        scale = 10  # scale of bounding rectangles

        # iterate through the entirety of the image (i.e. 30 bounding rectangles for scale 10)
        for i in range(30):
            size = i * scale  # size of current bounding rectangle

            # show bounding rectangle for user (unnecessary for program functionality)
            # cv.rectangle(img, (orgX - size, orgY - size), (orgX + size, orgY + size), (0,0,200), 1)
            # cv.imshow("Imaging Workbench", img)
            # cv.waitKey(30)

            # iterate through all current stars
            for ID, centroid in self.objects.items():

                # if the centroid falls into the bounding rectangle defined by the four points:
                #       1. (orgX - size, orgY - size)
                #       2. (orgX - size, orgY + size)
                #       3. (orgX + size, orgY - size)
                #       4. (orgX + size, orgY + size)
                if orgX - size < centroid[0] < orgX + size \
                        and orgY - size < centroid[1] < orgY + size:
                    # update the current trackStar and status
                    self.setTrackStar({ID:centroid})
                    self.mode = self.LOCKED
                    return img

        self.mode = self.SEARCHING  # reset mode to SEARCHING if we can't find a star
        return img

    ####################################################################
    def register(self, centroid):
        """Register a centroid to be tracked"""
        # when registering an object we use the next available object
        # ID to store the centroid
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    ####################################################################
    def deregister(self, objectID):
        """Deregister a centroid to stop being tracked"""
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[objectID]
        del self.disappeared[objectID]

    ####################################################################
    def update(self, inputCentroids):
        """Perform regular update of CentroidTracker given inputCentroids"""

        # update the self.objects and self.disappeared
        self.update_centroids(inputCentroids)

        # update the guiding status based on the trackStar
        self.update_status()

        # update the trackStar center of mass
        if self.mode is self.LOCKED:
            return self.update_trackstar()

        # return zero displacement when SEARCHING to maintain current trajectory
        return 0, 0

    ####################################################################
    def update_status(self):
        """Update the status of the tracking depending on the disappearance
        of trackStar."""

        # if the trackStar is being tracked...
        if self.getTrackStar()[0] in list(self.objects.keys()):
            self.mode = self.LOCKED
            return

        # trackStar was lost for one frame, start searching (not currently implemented)
        elif self.mode is self.LOST:
            self.mode = self.SEARCHING
            return

        # trackStar is not being tracked
        else:
            self.mode = self.SEARCHING
            return

    ####################################################################
    def update_trackstar(self):
        """Update trackStar location from self.objects and calculate
        displacement from the center point to the current trackStar."""

        # remember the old trackStar for calculating displacement
        oldTrackStar = self.getTrackStar()
        (ID, oldCentroid) = (oldTrackStar[0], oldTrackStar[1])

        # if we're currently locked onto a star...
        if self.mode is self.LOCKED:
            newCentroid = self.objects[ID]

            # displacement = newCentroid - centerPoint
            (dx, dy) = (newCentroid[0] - CentroidTracker.orgX,
                        CentroidTracker.orgY - newCentroid[1])

            # update the trackStar to reflect its new center of mass
            self.setTrackStar({ID: newCentroid})
            print(f"\t\tDisplacement: ({dx}, {dy})")
            return dx, dy
        else:
            print("\t<ERR: No star being tracked, exiting (unreachable).>")
            exit()

    ####################################################################
    def update_centroids(self, inputCentroids):
        """Match old centroids to a list of new centroids, update objects
        and disappeared objects accordingly"""
        # check to see if the list of input centroids is empty
        if len(inputCentroids) == 0:
            # loop over any existing tracked stars and mark them as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given star has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            return self.objects

        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i])

        # otherwise, we are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            D = dist.cdist(np.array(objectCentroids), inputCentroids)

            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value is at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in usedRows or col in usedCols:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0

                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unusedRows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants deregistering the object
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            else:
                for col in unusedCols:
                    self.register(inputCentroids[col])

        # return the set of trackable objects
        return self.objects

##############################################################################
