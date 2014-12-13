from lxml import objectify
from tcxparser import TCXParser

from datetime import datetime

from math import radians, cos, sin, asin, sqrt

import matplotlib.pyplot as plt

import numpy as np

from scipy.interpolate import interp1d

class Data:

    _latitudeValues = []
    _longtitudeValues = []
    _timestampValues = []
    _numberOfRawDataValues = 0

    distanceInEachTick = []
    accumulatedDistance = []
    timeOfEachTick = []
    accumulatedTime = []
    speedInEachTick = []
    numberOfCalculatedDataValues = 0

    def __init__(self):
        self._latitudeValues = []
        self._longtitudeValues = []
        self._timestampValues = []
        self.distanceInEachTick = []
        self.accumulatedDistance = []
        self.timeOfEachTick = []
        self.accumulatedTime = []
        self.speedInEachTick = []
        self._numberOfRawDataValues = 0
        self.numberOfCalculatedDataValues = 0

    def addNewTrackPoint(self, latitudeValue, longtitudeValue, timestampValue):
        self._latitudeValues.append(latitudeValue)
        self._longtitudeValues.append(longtitudeValue)
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
            distance = haversine(self._longtitudeValues[i], self._latitudeValues[i], self._longtitudeValues[i+1], self._latitudeValues[i+1])
            self.distanceInEachTick.append(distance)
            sumOfDistance += distance
            self.accumulatedDistance.append(sumOfDistance)
            lapTime = (timeList[i+1] - timeList[i]).total_seconds()
            self.timeOfEachTick.append(lapTime)
            sumOfTime += lapTime
            self.accumulatedTime.append(sumOfTime)
            speed = distance / lapTime
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




# http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points/4913653#4913653
# found by wikipedia link
def haversine( lon1, lat1, lon2, lat2):
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


tcx = TCXParser("F:/Projects/VS_2013/python_tcxVisualizer/data/endomondo_altitude_test.tcx")
tcxData = Data()

latitudeList = []
longtitudeList = []
timeList = []

for trackpoint in tcx.Trackpoints:
    #print(trackpoint.Position.LatitudeDegrees.pyval)
    latitudeList.append(trackpoint.Position.LatitudeDegrees.pyval)
    longtitudeList.append(trackpoint.Position.LongitudeDegrees.pyval)
    #timeList.append(trackpoint.Time.pyval)
    timeList.append(datetime.strptime(trackpoint.Time.pyval, '%Y-%m-%dT%H:%M:%SZ'))
    tcxData.addNewTrackPoint(trackpoint.Position.LatitudeDegrees.pyval, trackpoint.Position.LongitudeDegrees.pyval, trackpoint.Time.pyval)
#print(latitudeList)

for i in range(0, tcxData._numberOfRawDataValues):
    if latitudeList[i] != tcxData._latitudeValues[i]:
        print('Error latitude\r\n')
    if longtitudeList[i] != tcxData._longtitudeValues[i]:
        print('Error longtitude\r\n')
    if timeList[i] != tcxData._timestampValues[i]:
        print('Error timestamp\r\n')

distancesList = []
lapTimeList = []
for i in range(0, len(latitudeList)-1):
    distance = haversine(longtitudeList[i], latitudeList[i], longtitudeList[i+1], latitudeList[i+1])
    distancesList.append(distance)
    lapTime = (timeList[i+1] - timeList[i])
    lapTimeList.append(lapTime.total_seconds())

tcxData.calculateDistanceAndTimeAndSpeed()

for i in range(0, tcxData.numberOfCalculatedDataValues):
    if distancesList[i] != tcxData.distanceInEachTick[i]:
        print('Error distance\r\n')
    if lapTimeList[i] != tcxData.timeOfEachTick[i]:
        print('Error lapTime\r\n')

speedList = []
for i in range(len(distancesList)):
    speed = distancesList[i] / lapTimeList[i]
    # convert from m/s to km/h
    speed = speed * ((60*60)/1000)
    speedList.append(speed)

for i in range(0, tcxData.numberOfCalculatedDataValues):
    if speedList[i] != tcxData.speedInEachTick[i]:
        print('Error speed\r\n')

totalDistance = sum(distancesList)
totalTime = sum(lapTimeList)

print('Number of: \n' + 'latitude points: ' + str(len(latitudeList)) + '\n' + 'longtitude points: ' + str(len(longtitudeList)) + '\n')
print('Number of raw data in TCX object: ' + str(tcxData._numberOfRawDataValues) + '\n')
print('Number of: \n' + 'distance points: ' + str(len(distancesList)) + '\n' + 'lapTime points: ' + str(len(lapTimeList)) + '\n')
print('Number of calculated data in TCX object: ' + str(tcxData.numberOfCalculatedDataValues) + '\n')

print('Calculated distance: ' + str(totalDistance) + ', from file: ' + str(tcx.DistanceMeters) + ', from tcx object:' + str(tcxData.GetTotalDistance()) + '\n')
diff_time_last_point_first_point = (timeList[-1] - timeList[0]).total_seconds()
print('Calculated time: ' + str(totalTime) + ', fromFile: ' + str(tcx.TotalTimeSeconds) + ', last_point-first_point: ' + str(diff_time_last_point_first_point) + '\n' + ', from tcx object:' + str(tcxData.GetTotoalTime()) + ', from tcx object diff:' + str(tcxData.GetTotalTimeFromDifferemceBetweenFirstAndLastTimeStamp()) + '\n')

x = np.arange(0, 256, 1)

f = interp1d(x, distancesList)

x_new = np.arange(0., 255., 0.5)
newDistance = f(x_new)

plt.plot(x, distancesList, 'r', x, lapTimeList, 'b')
plt.ylabel('distance [m] - red, time [s] - blue')
plt.show()

plt.plot(speedList)
plt.ylabel('speed [km/h]')
plt.show()


print(haversine(0, 0, 0, 180)/1000)

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
