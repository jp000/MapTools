import math
import os
import re
import json
from datetime import datetime
from types import SimpleNamespace as Namespace


def Process(filename, full=False):
    dt = re.sub(r'\.\d+$', 'Z', datetime.utcnow().isoformat())
    filename = os.path.abspath(filename)
    geoJson = json.load(open(filename, 'r', encoding='utf-8'), object_hook=lambda d: Namespace(**d))
    nodes = {}
    for element in geoJson.elements:
        if element.type == 'node':
            nodes[element.id] = element.lon, element.lat

    data = []
    print('Processed {} nodes'.format(len(nodes)))
    for element in geoJson.elements:
        if element.type == 'way':
            way = []
            for node in element.nodes:
                n = nodes[node]
                way.append((n[0], n[1]))
            data.append(way)

    print('Processed {} ways'.format(len(data)))

    outputName = os.path.splitext(filename)[0] + '.geojson'
    with open(outputName, 'w', encoding='utf8') as fp:
        json.dump(GenJson(data, full), fp=fp, indent=2)

def GenJson(data, full):
    if full:
        out = {
        "type": "FeatureCollection",
        "features": [{
                    "type": "Feature",
                    "properties": {"stroke": "red"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [(lon, lat) for lon, lat in d]
                    }
                } for d in data]
        }
    else:
        out = {
        "type": "FeatureCollection",
        "features": [{
                    "type": "Feature",
                    "properties": {"stroke": "red"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [(d[0][0], d[0][1]),(d[-1][0], d[-1][1]) ]
                    }
                } for d in data]
        }
    return out

if __name__ == '__main__':
    import wx
    '''
        data=[out:json][timeout:900][maxsize:1073741824];  
        rel[["name"~"GR 5 ",i][type=route][route=hiking](35.88905,-9.58008,54.21386,20.03906);
        way(r);
        out body;
        node(w);
        out body;
    '''
    import sys
    if len(sys.argv) > 1:
        Process(sys.argv[1], True)
    else:
        app = wx.App(0)
        with wx.FileDialog(None, "Select a file", wildcard='OSM|*.osm|All (*.*)|*.*') as dlg:
            dlg.FilterIndex = 0
            dlg.ShowModal()
            if dlg.GetPath() == '':
                sys.exit(1)
            Process(dlg.GetPath(), True)
