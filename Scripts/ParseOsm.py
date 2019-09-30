from __future__ import print_function
import xml.sax

class OsmWayHandler(object, xml.sax.ContentHandler):
    def __init__(self):
        super(OsmWayHandler, self).__init__()
        self.result = {}
        self.index = 0;

    def startElement(self, name, attrs):
        if name == 'member' and attrs['type'] == 'way' and attrs['role'] == '':
            self.result[int(attrs['ref'])] = self.index
            self.index += 1


class OsmMapHandler(object, xml.sax.ContentHandler):
    def __init__(self, refs):
        super(OsmMapHandler, self).__init__()
        self.result = {}
        self.refs = refs
        self.gotWay = False
        self.nodes = []
        self.currentIdx = 0

    def startElement(self, name, attrs):
        if name == 'way':
            id = int(attrs['id'])
            if id in self.refs:
                self.gotWay = True;
                self.currentIdx = self.refs[id]
                self.nodes = []
        elif self.gotWay and name == 'nd':
            self.nodes.append(int(attrs['ref']))

    def endElement(self, name):
        if name == 'way' and self.gotWay:
            self.gotWay = False
            self.result[self.currentIdx] = self.nodes

class OsmNodeHandler(object, xml.sax.ContentHandler):
    def __init__(self, refs):
        super(OsmNodeHandler, self).__init__()
        self.refs = refs
        self.result = {}

    def startElement(self, name, attrs):
        if name == 'node':
            id = int(attrs['id'])
            nodeId = self.findNodeIndex(id)
            if nodeId  is not None:
                print(nodeId)
                self.result[nodeId] = (float(attrs['lat']), float(attrs['lon']))

    def findNodeIndex(self, value):
        for x in self.refs.keys():
            if value in self.refs[x]:
                return x
        return None

name = r'c:\Usr\Maps\Test\3Rivieres'

parser = xml.sax.make_parser()
wayHandler = OsmWayHandler()
parser.setContentHandler(wayHandler)
parser.parse(open(name + '.xml', 'r'))

print(wayHandler.result)

mapHandler = OsmMapHandler(wayHandler.result)
parser.setContentHandler(mapHandler)
parser.parse(open(name + '.osm', 'r'))

nodeHandler = OsmNodeHandler(mapHandler.result)
parser.setContentHandler(nodeHandler)
parser.parse(open(name + '.osm', 'r'))
print(nodeHandler.result)