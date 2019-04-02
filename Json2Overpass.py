# coding=utf-8
from __future__ import print_function
import json
import textwrap


# http://geojson.io/#map=2/20.0/0.0
# https://tools.ietf.org/html/rfc7946#section-1.4

def swapList(lst, elements=2):
    R = []
    for n in range(0, len(lst), elements):
        R.append(lst[n + 1])
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
            try:
                R.append('{}:&bbox={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in feature.geometry.bbox])))
                R.append(
                    '{}:({})'.format(name, ','.join(['{0:.5f}'.format(x) for x in swapList(feature.geometry.bbox)])))
            except AttributeError:
                pass
            for coordinates in feature.geometry.coordinates:
                poly = []
                for lng, lat in coordinates:
                    poly.append(float(lat))
                    poly.append(float(lng))

                w = textwrap.fill(' '.join(['{0:.5f}'.format(x) for x in poly]), width=120, break_long_words=False,
                                  break_on_hyphens=False)
                R.append('{}:node(poly:"{}");'.format(role, w))

        if feature.geometry.type == 'LineString':
            try:
                R.append('{}:&bbox={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in feature.geometry.bbox])))
                R.append(
                    '{}:({})'.format(name, ','.join(['{0:.5f}'.format(x) for x in swapList(feature.geometry.bbox)])))
            except AttributeError:
                pass
            lst = []
            for coordinates in feature.geometry.coordinates:
                lst.extend(coordinates)
            if len(coordinates) == 2:
                R.append('{}:[lng, lat]={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in lst])))
                R.append('{}:[lat, lng]={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in swapList(lst)])))
            if len(coordinates) == 3:
                R.append('{}:[lng, lat, ele]={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in lst])))
                R.append('{}:[lat, lng, ele]={}'.format(name, ','.join(['{0:.5f}'.format(x) for x in swapList(lst, 3)])))

        if feature.geometry.type == 'Point':
            lst = []
            for coordinates in feature.geometry.coordinates:
                lst.append(coordinates)
            R.append('{}:[lat, lng]={} "{}"'.format(name, ','.join(['{0:.5f}'.format(x) for x in swapList(lst)]),
                                                    description))

    return R


if __name__ == '__main__':
    import sys
    import wx
    import pprint

    try:
        from types import SimpleNamespace as Namespace
    except ImportError:
        # Python 2.x fallback
        from argparse import Namespace

    if len(sys.argv) > 1:
        f = sys.argv[1]
    else:
        app = wx.App(0)
        with wx.FileDialog(None, "Select a file", wildcard='GEOJSON|*.geojson|All (*.*)|*.*',
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            dlg.FilterIndex = 0
            dlg.ShowModal()
            if dlg.GetPath() == '':
                sys.exit(1)
            f = dlg.GetPath()

        J1 = json.load(open(f, 'r', encoding='utf-8'), object_hook=lambda d: Namespace(**d))
        for entry in processData(J1):
            print(entry)
