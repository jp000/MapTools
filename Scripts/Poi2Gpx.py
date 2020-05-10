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
        <time>{0}</time>
        <name>{3}</name>
        <cmt>{4}</cmt>
        <sym>{5}</sym>
        <extensions>
            <gpxx:WaypointExtension>
                <gpxx:Proximity>{6}</gpxx:Proximity>
                <gpxx:DisplayMode>SymbolAndName</gpxx:DisplayMode>
            </gpxx:WaypointExtension>
        </extensions>
      </wpt>
    '''
    template20 = '''<wpt lat="{1:.5f}" lon="{2:.5f}">
        <time>{0}</time>
        <name>{3}</name>
        <cmt>{4}</cmt>
        <sym>{5}</sym>
      </wpt>
    '''
    template3 = '</gpx>'
    template2a = '''  <rte>
        <name>{0}</name>
    '''
    template2b = '''    <rtept lat="{0:.5f}" lon="{1:.5f}">
            <name>{2}</name>
        </rtept>
    '''
    template2c = '''  </rte>
    '''

    dt = re.sub(r'\.\d+$', 'Z', datetime.utcnow().isoformat())
    filename = os.path.abspath(filename)
    geoJson = json.load(open(filename, 'r', encoding='utf-8'), object_hook=lambda d: Namespace(**d))
    outputName = os.path.splitext(filename)[0] + '_poi.gpx'
    nameIdx = 1
    with open(outputName, 'w', encoding='utf8') as fp:
        fp.write(template1.format(dt))
        for feature in geoJson.features:
            if feature.geometry.type == 'Point':
                cmt = getattr(feature.properties, 'description', '')
                if cmt == '':
                    cmt = getattr(feature.properties, 'desc', '')
                    if cmt == '':
                        cmt = getattr(feature.properties, 'info', '')
                symbol = getattr(feature.properties, 'marker-symbol', '')
                alarm = getattr(feature.properties, 'alarm', '')
                if symbol == '':
                    symbol = 'Waypoint'
                name = getattr(feature.properties, 'name', '')
                if name == '':
                    name = '{:03d}'.format(nameIdx)
                    nameIdx += 1
                if alarm:
                    fp.write(template2.format(dt, feature.geometry.coordinates[1], feature.geometry.coordinates[0],
                                          name, cmt, symbol, alarm))
                else:
                    fp.write(template20.format(dt, feature.geometry.coordinates[1], feature.geometry.coordinates[0],
                                          name, cmt, symbol))
        fp.write(template3)
        print('Created: {}'.format(outputName))

    outputName = os.path.splitext(filename)[0] + '_route.gpx'
    routeName = os.path.basename(os.path.splitext(filename)[0])
    nameIdx = 1
    with open(outputName, 'w', encoding='utf8') as fp:
        fp.write(template1.format(dt))
        fp.write(template2a.format(routeName))
        for feature in geoJson.features:
            if feature.geometry.type == 'Point':
                name = getattr(feature.properties, 'name', '')
                if name == '':
                    name = '{:03d}'.format(nameIdx)
                    nameIdx += 1
                fp.write(template2b.format(feature.geometry.coordinates[1], feature.geometry.coordinates[0], name))
        fp.write(template2c)
        fp.write(template3)
        print('Created: {}'.format(outputName))


if __name__ == '__main__':
    import sys, wx

    app = wx.App(0)
    with wx.FileDialog(None, "Select a file", wildcard='GEOJSON|*.geojson|All (*.*)|*.*',
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
        dlg.FilterIndex = 0
        dlg.ShowModal()
        if dlg.GetPath() == '':
            sys.exit(1)
        processPoi(dlg.GetPath())
