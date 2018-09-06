# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import xml.etree.ElementTree as ET
import math, sys
import win32clipboard

'''
Given a gpx file, find all bounding boxes of a given surface
'''

class BoundingBox(object):
    """
    A 2D bounding box
    """
    def __init__(self):
        self.sw_lng, self.sw_lat = float("inf"), float("inf")
        self.ne_lng, self.ne_lat = float("-inf"), float("-inf")
        self.count = 0

    def addPoint(self, x, y):
            self.count += 1
            # Set min coords
            if x < self.sw_lng:
                self.sw_lng = x
            if y < self.sw_lat:
                self.sw_lat = y
            # Set max coords
            if x > self.ne_lng:
                self.ne_lng = x
            elif y > self.ne_lat:
                self.ne_lat = y

    @property
    def w_lng(self):
        return self.ne_lng - self.sw_lng

    @property
    def w_lat(self):
        return self.ne_lat - self.sw_lat

    @property
    def distance_lng(self):
        try:
            a = (self.ne_lat + self.sw_lat)/2.0
            return self.w_lng * math.cos(math.radians(a)) * 111.0
        except ValueError:
            return 0.0

    @property
    def distance_lat(self):
        try:
            return self.w_lat * 111.0
        except ValueError:
            return 0.0

    @property
    def surface(self):
        return self.distance_lng * self.distance_lat

    def __repr__(self):
        return "BoundingBox({}, {}, {}, {})".format(
            self.sw_lng, self.ne_lng, self.sw_lat, self.ne_lat)

def parseGpx(filname, maxSurface):
    ns = '{http://www.topografix.com/GPX/1/1}'
    data = []
    with open(filname, 'r') as xml_file:
        tree = ET.parse(xml_file)

    root = tree.getroot()
    for trk in root.findall('{}{}'.format(ns, 'trk')):
        name = trk.find('{}{}'.format(ns, 'name')).text
        index = 0
        for trkseg in trk.findall('{}{}'.format(ns, 'trkseg')):
            b = BoundingBox()
            index += 1
            for trkpt in trkseg.findall('{}{}'.format(ns, 'trkpt')):
                b.addPoint(float(trkpt.get('lon')), float(trkpt.get('lat')))
                if b.surface > maxSurface:
                    data.append((name + '_' + str(index), b))
                    index += 1
                    b = BoundingBox()
            if b.count > 1:
                data.append((name + '_' + str(index), b))

    return data

def parseGpx1(filname, maxSurface):
    ns = '{http://www.topografix.com/GPX/1/1}'
    data = []
    with open(filname, 'r') as xml_file:
        tree = ET.parse(xml_file)

    root = tree.getroot()
    b = BoundingBox()
    index = 0
    name = 'Track'

    for trk in root.findall('{}{}'.format(ns, 'trk')):
        for trkseg in trk.findall('{}{}'.format(ns, 'trkseg')):
            for trkpt in trkseg.findall('{}{}'.format(ns, 'trkpt')):
                b.addPoint(float(trkpt.get('lon')), float(trkpt.get('lat')))
                if b.surface > maxSurface:
                    data.append((name + '_' + str(index), b))
                    index += 1
                    b = BoundingBox()
    if b.count > 1:
        data.append((name + '_' + str(index), b))
    return data


def Format(b, name):
    return 'https://extract.bbbike.org/?sw_lng={0:.3f}&sw_lat={1:.3f}&ne_lng={2:.3f}&ne_lat={3:.3f}&format=osm.xz&city={4}&lang=en'.format(b.sw_lng, b.sw_lat, b.ne_lng, b.ne_lat, name)

def CopyClip(data):
    win32clipboard.OpenClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, data)
    win32clipboard.CloseClipboard()


# Usage example:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        size = float(sys.argv[2]) if len(sys.argv) > 2 else 4000.0
        results = parseGpx1(sys.argv[1], size)
        for result in results:
            b = result[1]
            print('{} w={} h={} dx={} dy={}, s={}'.format(result, b.w_lng, b.w_lat, b.distance_lng, b.distance_lat, b.surface)   )
        for result in results:
            s = result[0]
            print(Format(result[1], s))
        CopyClip('\n'.join([Format(x[1], x[0]) for x in results]))
