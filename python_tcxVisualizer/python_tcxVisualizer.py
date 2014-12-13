from lxml import objectify
from tcxparser import TCXParser

from datetime import datetime

from math import radians, cos, sin, asin, sqrt

import matplotlib.pyplot as plt

import numpy as np

from scipy.interpolate import interp1d

import math
import bisect


class Data:

    def __init__(self):
        self._latitudeValues = []
        self._longtitudeValues = []
        self._altitudeValues = []
        self._timestampValues = []
        self.distanceInEachTick = []
        self.accumulatedDistance = []
        self.timeOfEachTick = []
        self.accumulatedTime = []
        self.speedInEachTick = []
        self._numberOfRawDataValues = 0
        self.numberOfCalculatedDataValues = 0

    def addNewTrackPoint(self, latitudeValue, longtitudeValue, timestampValue, altitudeValue):
        self._latitudeValues.append(latitudeValue)
        self._longtitudeValues.append(longtitudeValue)
        self._altitudeValues.append(altitudeValue)
        self._timestampValues.append(datetime.strptime(timestampValue, '%Y-%m-%dT%H:%M:%SZ'))
        self._numberOfRawDataValues += 1

    # http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points/4913653#4913653
    # found by wikipedia link
    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 

        # 6367 km is the radius of the Earth
        km = 6367 * c
        # result is returned in meters
        m = km * 1000
        return m

    def calculateDistanceAndTimeAndSpeed(self):
        sumOfDistance = 0
        sumOfTime = 0
        for i in range(0, self._numberOfRawDataValues-1):
            distance2d = self.haversine(self._longtitudeValues[i], self._latitudeValues[i], self._longtitudeValues[i+1], self._latitudeValues[i+1])
            height = abs(self._altitudeValues[i] - self._altitudeValues[i+1])
            distance3d = math.sqrt(distance2d**2 + height**2)
            self.distanceInEachTick.append(distance3d)
            sumOfDistance += distance3d
            self.accumulatedDistance.append(sumOfDistance)
            lapTime = (self._timestampValues[i+1] - self._timestampValues[i]).total_seconds()
            self.timeOfEachTick.append(lapTime)
            sumOfTime += lapTime
            self.accumulatedTime.append(sumOfTime)
            speed = distance3d / lapTime
            # convert from m/s to km/h
            speed = speed * ((60*60)/1000)
            self.speedInEachTick.append(speed) 
            self.numberOfCalculatedDataValues += 1

    def GetTotoalTime(self):
        return self.accumulatedTime[-1]

    def GetTotalDistance(self):
        return self.accumulatedDistance[-1]

    def GetTotalTimeFromDifferemceBetweenFirstAndLastTimeStamp(self):
        totalTime = (self._timestampValues[-1] - self._timestampValues[0]).total_seconds()
        return totalTime

    def GetLapTimesForRequestedDistance_C_way(self, requestedDistance):
        index = 0
        flagFinished = False
        accumulatedDistance = 0
        accumulatedTime = 0
        while (flagFinished == False):
            currentStepDistance = self.distanceInEachTick[index]
            currentStepTime = self.timeOfEachTick[index]
            if (accumulatedDistance+currentStepDistance) < requestedDistance:
                accumulatedDistance += currentStepDistance
                accumulatedTime += currentStepTime
                index += 1
            else:
                missingDistance = requestedDistance - accumulatedDistance
                currentStepSpeed = self.speedInEachTick[index]
                if currentStepSpeed == 0:
                    currentStepSpeed = 0.1
                accumulatedTime += missingDistance / currentStepSpeed
                flagFinished = True
        return accumulatedTime

    def GetLapTimesForRequestedDistance(self, requestedDistance):
        indexOfClosestElement = bisect.bisect_right(self.accumulatedDistance, requestedDistance)-1
        missingDistance = requestedDistance - self.accumulatedDistance[indexOfClosestElement]
        currentStepSpeed = self.speedInEachTick[indexOfClosestElement]
        # TODO - adde the possibility of stops during the run
        interpolatedTime = 0
        if currentStepSpeed != 0:
            interpolatedTime = missingDistance / currentStepSpeed
        return self.accumulatedTime[indexOfClosestElement] + interpolatedTime

            


tcx = TCXParser("F:/Projects/VS_2013/python_tcxVisualizer/data/endomondo_altitude_test.tcx")
tcxData = Data()


for trackpoint in tcx.Trackpoints:
    tcxData.addNewTrackPoint(trackpoint.Position.LatitudeDegrees.pyval, trackpoint.Position.LongitudeDegrees.pyval, trackpoint.Time.pyval, trackpoint.AltitudeMeters.pyval)

tcxData.calculateDistanceAndTimeAndSpeed()

print('Number of raw data in TCX object: ' + str(tcxData._numberOfRawDataValues) + '\n')
print('Number of calculated data in TCX object: ' + str(tcxData.numberOfCalculatedDataValues) + '\n')

print('Total distance: from file: ' + str(tcx.DistanceMeters) + ', calculated from raw data:' + str(tcxData.GetTotalDistance()) + '\n')
print('Total time:  fromFile: ' + str(tcx.TotalTimeSeconds) + ', calculated from raw data:' + str(tcxData.GetTotoalTime()) + ', last_timestamp-first_timestamp:' + str(tcxData.GetTotalTimeFromDifferemceBetweenFirstAndLastTimeStamp()) + '\n')

for item in tcxData.speedInEachTick:
    if item < 0.01:
        print("Error")

for i in range(0, 6000, 500):
    print(tcxData.GetLapTimesForRequestedDistance(i))
    print('\n')

x = np.arange(0, 256, 1)

f = interp1d(x, tcxData.distanceInEachTick)

x_new = np.arange(0., 255., 0.5)
newDistance = f(x_new)

plt.plot(x, tcxData.distanceInEachTick, 'r', x, tcxData.timeOfEachTick, 'b')
plt.ylabel('distance [m] - red, time [s] - blue')
plt.show()

plt.plot([60/(x) if x!=0 else 0 for x in tcxData.speedInEachTick])
plt.gca().invert_yaxis()
plt.ylabel('speed [km/min]')
plt.show()

plt.plot(tcxData.speedInEachTick)
plt.ylabel('speed [km/h]')
plt.show()


#print(haversine(0, 0, 0, 180)/1000)

namespace = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'

# http://infohost.nmt.edu/tcc/help/pubs/pylxml/web/index.html
object = objectify.parse("F:/Projects/VS_2013/python_tcxVisualizer/data/endomondo_altitude_test.tcx")
print(object)
root = object.getroot()
print(root)
activity = root.Activities.Activity
print(activity)

activity_type = activity.attrib['Sport'].lower()
print(activity_type)

latitude = activity.Lap.Track.Trackpoint[200].Position.LatitudeDegrees.pyval
print(latitude)





print('Hello World')
