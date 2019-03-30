# coding=utf-8
from __future__ import print_function
import json
import textwrap


# http://geojson.io/#map=2/20.0/0.0
# https://tools.ietf.org/html/rfc7946#section-1.4

def swapList(lst):
    R = []
    for n in range(0, len(lst), 2):
        R.append(lst[n+1])
        R.append(lst[n])
    return R


def processData(geoJson):
    R = []

    if hasattr(geoJson, 'bbox'):
        print('main:&bbox={}'.format(','.join(['{0:.5f}'.format(x) for x in J1.bbox])))

    for feature in geoJson.features:
        R.append('Feature = {}'.format(feature.geometry.type))

        if feature.geometry.type == 'MultiPoint':
            continue
        if feature.geometry.type == 'MultiLineString':
            continue
        if feature.geometry.type == 'MultiPolygon':
            continue
        if feature.geometry.type == 'GeometryCollection':
            continue

        role = getattr(feature.properties, 'role', '')
        name = getattr(feature.properties, 'name', '')
        description = getattr(feature.properties, 'description', '')
        if description == '':
            description = getattr(feature.properties, 'desc', '')
            if description == '':
                description = getattr(feature.properties, 'info', '')

        if feature.geometry.type == 'Polygon':
            for coordinates in feature.geometry.coordinates:
                poly = []
                for lng, lat in coordinates:
                    poly.append(float(lat))
                    poly.append(float(lng))

                w = textwrap.fill(' '.join(['{0:.5f}'.format(x) for x in poly]), width=120, break_long_words=False,
                                  break_on_hyphens=False)
                R.append('{}:node(poly:"{}");'.format(role, w))

        if feature.geometry.type == 'LineString':
            lst = []
            for coordinates in feature.geometry.coordinates:
                lst.extend(coordinates)
            if len(lst) == 4:
                R.append('{}:&bbox={}'.format(name,','.join(['{0:.5f}'.format(x) for x in lst])))
            else:
                R.append('{}:[lng, lat]={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in lst])))
                R.append('{}:[lat, lng]={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in swapList(lst)])))

        if feature.geometry.type== 'Point':
            lst = []
            for coordinates in feature.geometry.coordinates:
                lst.append(coordinates)
            R.append('{}:[lat, lng]={} "{}"'.format(name, ','.join(['{0:.5f}'.format(x) for x in swapList(lst)]), description))

    return R


if __name__ == '__main__':
    import sys
    import pprint

    try:
        from types import SimpleNamespace as Namespace
    except ImportError:
        # Python 2.x fallback
        from argparse import Namespace

    if len(sys.argv) > 1:
        f = sys.argv[1]
        J1 = json.load(open(f, 'r', encoding='utf-8'), object_hook=lambda d: Namespace(**d))
        for entry in processData(J1):
            print(entry)
