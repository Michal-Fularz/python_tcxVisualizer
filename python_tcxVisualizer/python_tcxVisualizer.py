from lxml import objectify
from tcxparser import TCXParser

from datetime import datetime

from math import radians, cos, sin, asin, sqrt

import matplotlib.pyplot as plt

import numpy as np

# http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points/4913653#4913653
# found by wikipedia link
def haversine(lon1, lat1, lon2, lat2):
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

namespace = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'

tcx = TCXParser("F:/Projects/VS_2013/python_tcxVisualizer/data/endomondo_altitude_test.tcx")
print(tcx.latitude)
latitudeList = []
longtitudeList = []
timeList = []
for trackpoint in tcx.Trackpoints:
    #print(trackpoint.Position.LatitudeDegrees.pyval)
    latitudeList.append(trackpoint.Position.LatitudeDegrees.pyval)
    longtitudeList.append(trackpoint.Position.LongitudeDegrees.pyval)
    #timeList.append(trackpoint.Time.pyval)
    timeList.append(datetime.strptime(trackpoint.Time.pyval, '%Y-%m-%dT%H:%M:%SZ'))
#print(latitudeList)
print(timeList)
print('\r\n')

distancesList = []
lapTimeList = []
for i in range(0, len(latitudeList)-1):
    distance = haversine(longtitudeList[i], latitudeList[i], longtitudeList[i+1], latitudeList[i+1])
    distancesList.append(distance)
    lapTime = (timeList[i+1] - timeList[i])
    lapTimeList.append(lapTime.total_seconds())
print(distancesList)
print('\r\n')
print(lapTimeList)

speedList = []
for i in range(len(distancesList)):
    speed = distancesList[i] / lapTimeList[i]
    # convert from m/s to km/h
    speed = speed * ((60*60)/1000)
    speedList.append(speed)
print(speedList)

totalDistance = sum(distancesList)
totalTime = sum(lapTimeList)

print('Number of: \n' + 'latitude points: ' + str(len(latitudeList)) + '\n' + 'longtitude points: ' + str(len(longtitudeList)) + '\n')
print('Number of: \n' + 'distance points: ' + str(len(distancesList)) + '\n' + 'lapTime points: ' + str(len(lapTimeList)) + '\n')

print('Calculated distance: ' + str(totalDistance) + ', from file: ' + str(tcx.DistanceMeters) + '\r\n')
diff_time_last_point_first_point = (timeList[-1] - timeList[0]).total_seconds()
print('Calculated time: ' + str(totalTime) + ', fromFile: ' + str(tcx.TotalTimeSeconds) + ', last_point-first_point: ' + str(diff_time_last_point_first_point) + '\r\n')

xAxis = np.arange(0, 256, 1)

plt.plot(xAxis, distancesList, 'r', xAxis, lapTimeList, 'b')
plt.ylabel('distance [m] - red, time [s] - blue')
plt.show()

plt.plot(speedList)
plt.ylabel('speed [km/h]')
plt.show()


print(haversine(0, 0, 0, 180)/1000)

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
