# coding=utf-8
from __future__ import print_function

# http://geojson.io/#map=2/20.0/0.0

def createPolyNone(fileName):
    import json
    R = []
    J = json.load(open(f, 'r'), encoding='utf-8')
    for feature in J['features']:
        if feature['geometry']['type'] == 'Polygon':
            for coordinates in feature['geometry']['coordinates']:
                poly = []
                for lng, lat in coordinates:
                    poly.append(float(lat))
                    poly.append(float(lng))
                R.append('node(poly:"{}");'.format(' '.join(['{0:.5f}'.format(x) for x in poly])))
    return R

def swapList(lst):
    R = []
    for n in range(0, len(lst), 2):
        R.append(lst[n+1])
        R.append(lst[n])
    return R

def createLineString(fileName):
    import json
    R = []
    J = json.load(open(f, 'r'), encoding='utf-8')
    for feature in J['features']:
        if feature['geometry']['type'] == 'LineString':
            lst = []
            for coordinates in feature['geometry']['coordinates']:
                lst.extend(coordinates)
            if len(lst) == 4:
                R.append('&bbox={}'.format(','.join(['{0:.5f}'.format(x) for x in lst])))
            else:
                R.append('{}'.format(','.join(['{0:.5f}'.format(x) for x in lst])))
                R.append('{}'.format(','.join(['{0:.5f}'.format(x) for x in swapList(lst)])))
    return R

def createPoints(fileName):
    import json
    R = []
    J = json.load(open(f, 'r'), encoding='utf-8')
    for feature in J['features']:
        if feature['geometry']['type'] == 'Point':
            n = ''
            if 'name' in feature['properties']:
                n = feature['properties']['name']
            lst = []
            for coordinates in feature['geometry']['coordinates']:
                lst.append(coordinates)
            R.append('{}={}'.format(n, ','.join(['{0:.5f}'.format(x) for x in swapList(lst)])))
    return R

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        f = sys.argv[1]
        for entry in createPolyNone(f):
            print(entry)
        for entry in createLineString(f):
            print(entry)
        for entry in createPoints(f):
            print(entry)
