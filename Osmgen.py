import os, random
from time import strftime

hdr = '''<?xml version='1.0' encoding='UTF-8'?>
<osm version='0.6' generator='osm_generate'>
  <bounds minlat='{}' minlon='{}' maxlat='{}' maxlon='{}' origin='OSM_Generate' />\n'''

node = '''  <node id='{}' timestamp='{}' visible='true' lat='{:.8}' lon='{:.8}'>
    <tag k='point' v='p{:04d}' />
  </node>\n'''

pointdef = "point=p{0:04d} {{name '0X{1:04X}'}} [0X{1:04X} resolution 20]\n"
polydef = "poly=p{0:04d} {{set name='0X{1:02X}'}} [0X{1:02X} resolution 20]\n"


def getValues(minVal, maxVal, numpoints):
    delta = (maxVal - minVal) / numpoints
    r = []
    v = minVal + (delta / 2.0)
    for i in range(numpoints):
        r.append(v)
        v += delta
    return r


def processRandom(minLat, maxLat, minLon, maxLon, numpoints):
    ts = strftime('%Y-%m-%d %H:%M:%S')
    with open(r'c:\Usr\Maps\OsmGen\points.osm', 'w') as fp:
        fp.write(hdr.format(minLat, minLon, maxLat, maxLon))
        idx = 1
        for x in range(0, numpoints):
            fp.write(node.format(-idx, ts, random.uniform(minLat, maxLat), random.uniform(minLon, maxLon), idx))
            idx += 1
        fp.write('</osm>')


def processLinear(minLat, maxLat, minLon, maxLon, numpointsLat, numpointsLon):
    latitudes = getValues(minLat, maxLat, numpointsLat)
    longitudes = getValues(minLon, maxLon, numpointsLon)
    ts = strftime('%Y-%m-%d %H:%M:%S')
    with open(r'c:\Usr\Maps\OsmGen\points.osm', 'w') as fp:
        fp.write(hdr.format(minLat, minLon, maxLat, maxLon))
        idx = 1
        for lat in latitudes:
            for lon in longitudes:
                fp.write(node.format(-idx, ts, lat, lon, idx))
                idx += 1
        fp.write('</osm>')

pois = []
pois.extend([x << 8 for x in range(1, 0x12)])
pois.extend([x << 8 for x in range(0x22, 0x2a)])
pois.extend([(x << 8) + y for x in range(0x2a, 0x31) for y in range(32)])
pois.extend([(x << 8) + y for x in range(0x40, 0x59) for y in range(1)])
pois.extend([0x5900 + x for x in range(30)])
pois.extend([(x << 8) + y for x in range(0x64, 0x67) for y in range(32)])

#processRandom(47.0, 47.05, 7.0, 7.05, len(pois))
processLinear(47.0, 47.05, 7.0, 7.05, 25, 15)

with open(r'c:\Usr\Maps\OsmGen\E10\points', 'w') as fp:
    idx = 1
    for p in pois:
        fp.write(pointdef.format(idx, p))
        idx += 1
