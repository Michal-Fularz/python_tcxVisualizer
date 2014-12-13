from lxml import objectify
from tcxparser import TCXParser

namespace = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'

tcx = TCXParser("F:/Projects/VS_2013/python_tcxVisualizer/data/endomondo_altitude_test.tcx")
print(tcx.latitude)
latitudeList = []
for trackpoint in tcx.Trackpoints:
    #print(trackpoint.Position.LatitudeDegrees.pyval)
    latitudeList.append(trackpoint.Position.LatitudeDegrees.pyval)
print(latitudeList)



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
