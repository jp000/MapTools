from __future__ import print_function

import math
import os
import xml.sax

import requests

'''
Create a gpx file given a relation number.
This can be used by the script bbbikeExtract.py to create bounding boxes for the site extract.bbbike.org
'''

def GetRelation(number, fileName):
    if os.path.exists(fileName):
        return
    url = r'https://www.openstreetmap.org/api/0.6/relation/{0}/full'.format(number)
    r = requests.get(url)
    with open(fileName, 'w', encoding='utf-8') as out:
        #        out.write(r.content)
        out.write(r.content.decode('utf-8'))
    print('Created {}'.format(fileName))


class Node(object):
    version = None
    longitude = None
    latitude = None
    id = None
    extra = None
    tags = None

    def __init__(self, latitude, longitude, version, id):
        self.latitude = latitude
        self.longitude = longitude
        self.version = version
        self.id = id
        self.extra = None
        self.tags = {}

    def getDelta(self, previous=None):
        if previous is None:
            return 0.0
        a = (self.longitude - previous.longitude) * math.cos(
            math.radians((self.latitude + previous.latitude) / 2.0)) * 111.0
        b = (self.latitude - previous.latitude) * 111.0
        return math.sqrt(a ** 2 + b ** 2) * 1000.0

    def __str__(self):
        return '{}: {},{} ({})'.format(self.id, self.longitude, self.latitude, self.version)


class Way(object):
    nodes = None
    index = None
    version = None
    extra = None

    def __init__(self, index, version, nodes=None):
        self.version = version
        self.index = index
        self.nodes = [] if nodes is None else nodes
        self.extra = None

    def addNode(self, node):
        self.nodes.append(node)

    def __str__(self):
        return '{0} {1}'.format(self.index, str(self.nodes))


class OsmHandler(xml.sax.ContentHandler, object):
    def __init__(self):
        super(OsmHandler, self).__init__()
        self.wayRelations = []
        self.nodeRelations = []
        self.nodes = {}
        self.ways = {}
        self.wayIndex = 0
        self.wayId = None
        self.relationId = None
        self.relationName = None
        self.currentNode = None
        self.currentWay = None

    def startElement(self, name, attrs):
        if name == 'node' and attrs['visible'] == 'true':
            id = int(attrs['id'])
            v = int(attrs['version'])
            if id in self.nodes:
                print('duplicate in node at: {0}'.format(id))
                n = self.nodes[id]
                if n.version < v:
                    self.currentNode = Node(float(attrs['lat']), float(attrs['lon']), v, id)
                    self.nodes[id] = self.currentNode
            else:
                self.currentNode = Node(float(attrs['lat']), float(attrs['lon']), v, id)
                self.nodes[id] = self.currentNode

        elif name == 'way' and attrs['visible'] == 'true':
            self.wayId = int(attrs['id'])
            if self.wayId in self.ways:
                print('duplicate in way at: {0}'.format(self.wayId))
            else:
                self.currentWay = Way(self.wayIndex, int(attrs['version']))
                self.ways[self.wayId] = self.currentWay
                self.wayIndex += 1

        elif name == 'nd':
            if self.currentWay is not Node:
                self.currentWay.addNode(self.nodes[int(attrs['ref'])])

        elif name == 'member' and attrs['type'] == 'way' and attrs['role'] == '':
            id = int(attrs['ref'])
            if not id in self.ways:
                print("ref {} not found in ways".format(id))
            else:
                if self.ways[id] in self.wayRelations:
                    print('duplicate in relation member at: {0}'.format(id))
                self.wayRelations.append(self.ways[id])

        elif name == 'member' and attrs['type'] == 'node':
            id = int(attrs['ref'])
            if not id in self.nodes:
                print("ref {} not found in nodes".format(id))
            else:
                if self.nodes[id] in self.nodeRelations:
                    print('duplicate in nodeRelations member at: {0}'.format(id))
                self.nodeRelations.append(self.nodes[id])

        elif name == 'relation':
            self.relationId = attrs['id']

        elif name == 'tag':
            if self.relationId is not None:
                if attrs['k'] == 'name':
                    self.relationName = attrs['v']

            elif self.currentWay is not None:
                if self.currentWay.extra is None:
                    self.currentWay.extra = {}
                self.currentWay.extra[attrs['k']] = attrs['v']

            elif self.currentNode is not None:
                if self.currentNode.tags is None:
                    self.currentNode.tags = {}
                self.currentNode.tags[attrs['k']] = attrs['v']

    def endElement(self, name):
        if name == 'relation':
            self.relationId = None
        elif name == 'way':
            self.wayId = None
        elif name == 'node':
            self.currentNode = None


def CreateGpx(handler, fileName, approx, debug=False):
    template1 = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<gpx  xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" creator="eTrex 10" version="1.1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
  <trk>
    <name>{0}</name>
    <cmt>{1}</cmt>
'''
    template2 = u'      <trkpt lat="{0:.4f}" lon="{1:.4f}" />'
    template2d = u'      <trkpt lat="{0:.4f}" lon="{1:.4f}" delta="{2}" nodeid="{3}"/>'
    template3 = u'''  <wpt lat="{0:.5f}" lon="{1:.5f}">
    <ele>{2}</ele>
    <name>{3}</name>
    <cmt>{4}</cmt>
    <sym>{5}</sym>
	<extensions>
		<gpxx:WaypointExtension>
			<gpxx:Proximity>150</gpxx:Proximity>
		</gpxx:WaypointExtension>
	</extensions>
  </wpt>
'''
    with open(fileName, 'w', encoding='utf-8') as out:
        name = os.path.basename(fileName)
        name = os.path.splitext(name)[0]
        #        out.write(template1.format(name, '').encode('utf-8'))
        out.write(template1.format(name, ''))

        for x in handler.wayRelations:
            if x.nodes[0] == x.nodes[-1]:  # skip loops
                print("skip loop at {}".format(x.nodes[0]))
                continue
            if x.nodes[-1].getDelta(x.nodes[0]) < approx:  # skip small segments
                print("skip small segment at {}".format(x.nodes[0]))
                continue

            lineBuffer = []
            lineBuffer.append(u'    <trkseg>')
            previousNode = None
            for v in x.nodes:
                delta = v.getDelta(previousNode)
                if delta > 0.0 and delta < approx:  # skip if to near
                    print("skip small at {}".format(x.nodes[0]))
                    continue
                if debug:
                    lineBuffer.append(template2d.format(v.latitude, v.longitude, delta, v.id))
                else:
                    lineBuffer.append(template2.format(v.latitude, v.longitude))
                previousNode = v
            lineBuffer.append(u'    </trkseg>\n')
            if len(lineBuffer) > 3:  # skip if only one entry
                #                out.write('\n'.join(lineBuffer).encode('utf-8'))
                out.write('\n'.join(lineBuffer))
            else:
                pass

        #        out.write(u'  </trk>\n'.encode('utf-8'))
        out.write(u'  </trk>\n')

        for node in handler.nodeRelations:
            if node.tags is not None:
                ele = 0.0 if 'ele' not in node.tags else float(node.tags['ele'])
                if 'name' in node.tags:
                    txt = template3.format(node.latitude, node.longitude, ele, node.tags['name'], '', 'Flag, Green')
                    #                   out.write(txt.encode('utf-8'))
                    out.write(txt)

        for nodeid in handler.nodes:
            node = handler.nodes[nodeid]
            if len(node.tags) > 0 and 'information' in node.tags:
                name = 'information' if 'name' not in node.tags else node.tags['name']
                txt = template3.format(node.latitude, node.longitude, 0.0, name, '', 'Flag, Blue')
                #                   out.write(txt.encode('utf-8'))
                out.write(txt)

        #        out.write(u'</gpx>\n'.encode('utf-8'))
        out.write(u'</gpx>\n')


def Process(name, relation, approx, debug=False):
    GetRelation(relation, name + '.xml')
    parser = xml.sax.make_parser()
    myHandler = OsmHandler()
    parser.setContentHandler(myHandler)
    parser.parse(open(name + '.xml', 'r', encoding='utf-8'))
    print('{0} nodes, {1} ways, {2} relation members'.format(len(myHandler.nodes), len(myHandler.ways),
                                                             len(myHandler.wayRelations)))

    # w = [myHandler.ways[x] for x in sorted(myHandler.ways, key=lambda x: myHandler.ways[x].index)]
    # x = [myHandler.ways[x] for x in myHandler.ways]

    # CreateGpx(w, name + 'w.gpx')
    # CreateGpx(x, name + 'x.gpx')
    CreateGpx(myHandler, name + '.gpx', approx, debug)


if __name__ == '__main__':
    import sys
    # Process(r'c:\Usr\Maps\Test\GR5_Aples', 2704286, 80.0, False)
    Process(r'c:\Usr\Maps\Tmp\ViaRomeaFrancigena', 124582, 80, False)
    # Process(r'c:\Usr\Maps\Test\3Rivieres', 1718788, 30.0, False)
    # Process(r'c:\Usr\Maps\Test\GR20', 101692, 60, True)
