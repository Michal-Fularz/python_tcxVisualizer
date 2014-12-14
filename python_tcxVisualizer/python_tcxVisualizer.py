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

    def GetAverageSpeedInMinPerKm(self):
        avgSpeed = (self.GetTotoalTime() / self.GetTotalDistance()) * (1000.0/60.0)
        return avgSpeed

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

    def GetTimeForRequestedDistance(self, requestedDistance):
        indexOfClosestElement = bisect.bisect_right(self.accumulatedDistance, requestedDistance)-1
        missingDistance = requestedDistance - self.accumulatedDistance[indexOfClosestElement]
        currentStepSpeed = self.speedInEachTick[indexOfClosestElement]
        # TODO - adde the possibility of stops during the run
        interpolatedTime = 0.0
        if currentStepSpeed != 0:
            interpolatedTime = missingDistance / currentStepSpeed
        return self.accumulatedTime[indexOfClosestElement] + interpolatedTime

    def GetLapTimeForRequestedLapDistance(self, requestedLapDistance):
        return [self.GetTimeForRequestedDistance(x)-self.GetTimeForRequestedDistance(x-requestedLapDistance) for x in range(requestedLapDistance, 6001, requestedLapDistance)]

       

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
        print("Speed equal to 0")
print('\n')

#for i in range(500, 6000, 500):
#    print(tcxData.GetTimeForRequestedDistance(i))
#    print('\n')

#print(tcxData.GetLapTimeForRequestedLapDistance(500))

import datetime
#print('Time for each 500m: ')
#for item in tcxData.GetLapTimeForRequestedLapDistance(500):
#    print(str(datetime.timedelta(seconds=item)) + ', ')
#print('\n')

# correct the way 0 is calculated... currently returning 24 cause that's the time when I started moving according to endomondo
zeroLap = tcxData.GetTimeForRequestedDistance(0)
print('starting delay (zero lap): ' + str(datetime.timedelta(seconds=zeroLap)))
firstLap = tcxData.GetTimeForRequestedDistance(1000)-zeroLap

endomonodoTimes = []
endomonodoTimes.append(4*60 + 18)
endomonodoTimes.append(4*60 + 30)
endomonodoTimes.append(4*60 + 36)
endomonodoTimes.append(4*60 + 35)
endomonodoTimes.append(4*60 + 34)
endomonodoTimes.append(4*60 + 38)

print('Time for each 1000m: ')
zipped = zip(endomonodoTimes, tcxData.GetLapTimeForRequestedLapDistance(1000))
for tuple in zipped:
    print('Endomonodo: ' + str(datetime.timedelta(seconds=tuple[0])) + ', calculated: ' + str(datetime.timedelta(seconds=tuple[1])))
print('Time of rest: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(1*60+12))) + ', calculated: ' + str( datetime.timedelta(seconds=tcxData.GetTotoalTime() - tcxData.GetTimeForRequestedDistance(6000))) + '\n')


#print('Endomono time for each 1000m: ')
#for item in originalTimes:
#    print(str(datetime.timedelta(seconds=item)) + ', ')
#print('\n')

mileInKm = 1.609344
print('Times for different distances: \n')
print('1 km: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(3*60+54))) + ', calculated: ' + str(datetime.timedelta(seconds=tcxData.GetTimeForRequestedDistance(1000))))
print('1 mile: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(6*60+37))) + ', calculated: ' + str(datetime.timedelta(seconds=tcxData.GetTimeForRequestedDistance(1000*mileInKm))))
print('3 km: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(13*60+0))) + ', calculated: ' + str(datetime.timedelta(seconds=tcxData.GetTimeForRequestedDistance(3000))))
print('3 miles: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(21*60+25))) + ', calculated: ' + str(datetime.timedelta(seconds=tcxData.GetTimeForRequestedDistance(3000*mileInKm))))
print('5 km: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(22*60+9))) + ', calculated: ' + str(datetime.timedelta(seconds=tcxData.GetTimeForRequestedDistance(5000))))
print('Whole run: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(28*60+30))) + ', calculated: ' + str(datetime.timedelta(seconds=tcxData.GetTotoalTime())))
print('\n')
print('Average speed: ')
print('Endomonodo: ' + str(datetime.timedelta(seconds=(4*60+33))) + ', calculated: ' + str(datetime.timedelta(minutes=tcxData.GetAverageSpeedInMinPerKm())) + '\n')

x = np.arange(0, 256, 1)

f = interp1d(x, tcxData.distanceInEachTick)
x_new = np.arange(0., 255., 0.5)
newDistance = f(x_new)

x = np.arange(0, tcxData._numberOfRawDataValues, 1)

plt.plot(x, tcxData._longtitudeValues, 'r')
plt.ylabel('_longtitudeValues - red')
plt.show()

plt.plot(x, tcxData._latitudeValues, 'b')
plt.ylabel('_latitudeValues - blue')
plt.show()

plt.plot(x, tcxData._altitudeValues, 'g')
plt.ylabel('_altitudeValues - g')
plt.show()

x = np.arange(0, tcxData.numberOfCalculatedDataValues, 1)

plt.plot(x, tcxData.distanceInEachTick, 'r', x, tcxData.timeOfEachTick, 'b')
plt.ylabel('distance [m] - red, time [s] - blue')
plt.show()

plt.plot(x, tcxData.accumulatedDistance, 'r', x, tcxData.accumulatedTime, 'b')
plt.ylabel('accumulated distance [m] - red, accumulated time [s] - blue')
plt.show()

plt.plot([60/(x) if x!=0 else 0 for x in tcxData.speedInEachTick])
plt.gca().invert_yaxis()
plt.ylabel('speed [min/km]')
plt.show()

plt.plot(tcxData.speedInEachTick)
plt.ylabel('speed [km/h]')
plt.show()

# check the size of 0.5 of equator 
#print(haversine(0, 0, 0, 180)/1000)
