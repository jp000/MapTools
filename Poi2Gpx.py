import math
import os
import re
import json
from datetime import datetime
from types import SimpleNamespace as Namespace

# http://geojson.io/#map=2/20.0/0.0
# https://tools.ietf.org/html/rfc7946#section-1.4

def processPoi(filename):
    template1 = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" creator="eTrex 10" version="1.1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
      <metadata>
        <link href="http://www.garmin.com">
          <text>Garmin International</text>
        </link>
        <time>{0}</time>
      </metadata>
    '''
    template2 = '''<wpt lat="{1:.5f}" lon="{2:.5f}">
        <ele>{3:.1f}</ele>
        <time>{0}</time>
        <name>{4}</name>
        <cmt>{5}</cmt>
        <sym>{6}</sym>
    	<extensions>
    		<gpxx:WaypointExtension>
    			<gpxx:Proximity>{7}</gpxx:Proximity>
    		</gpxx:WaypointExtension>
    	</extensions>
      </wpt>
    '''
    template3 = '</gpx>'

    dt = re.sub(r'\.\d+$', 'Z', datetime.utcnow().isoformat())
    filename = os.path.abspath(filename)
    geoJson = json.load(open(filename, 'r', encoding='utf-8'), object_hook=lambda d: Namespace(**d))
    outputName = os.path.splitext(filename)[0] + '.gpx'
    with open(outputName, 'w', encoding='utf8') as fp:
        fp.write(template1.format(dt))
        for feature in geoJson.features:
            if feature.geometry.type == 'Point':
                cmt = getattr(feature.properties, 'description', '')
                if cmt == '':
                    cmt = getattr(feature.properties, 'desc', '')
                    if cmt == '':
                        cmt = getattr(feature.properties, 'info', '')

                fp.write(template2.format(dt, feature.geometry.coordinates[1], feature.geometry.coordinates[0], 0,
                                          getattr(feature.properties, 'name', ''),
                                          cmt,
                                          getattr(feature.properties, 'marker-symbol', 'Waypoint'), 100))
        fp.write(template3)

if __name__ == '__main__':
    processPoi('map.geojson')