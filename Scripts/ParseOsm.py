import xml.sax

class OsmWayHandler(xml.sax.ContentHandler):
    def __init__(self):
        super(OsmWayHandler, self).__init__()
        self.result = {}
        self.index = 0;

    def startElement(self, name, attrs):
        if name == 'member' and attrs['type'] == 'way' and attrs['role'] == '':
            self.result[int(attrs['ref'])] = self.index
            self.index += 1


class OsmMapHandler(xml.sax.ContentHandler):
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

class OsmNodeHandler(xml.sax.ContentHandler):
    def __init__(self, refs):
        super(OsmNodeHandler, self).__init__()
        self.refs = refs
        self.result = {}
        self.gotNode = False

    def startElement(self, name, attrs):
        if name == 'node':
            self.gotNode = True
            id = int(attrs['id'])
            nodeId = self.findNodeIndex(id)
            if nodeId  is not None:
                print(nodeId)
                self.result[nodeId] = (float(attrs['lat']), float(attrs['lon']))

    def endElement(self, name):
        if name == 'node':
            self.gotNode = False

    def findNodeIndex(self, value):
        for x in self.refs.keys():
            if value in self.refs[x]:
                return x
        return None

class OsmNodeHandler1(xml.sax.ContentHandler):
    def __init__(self, population=0):
        super(OsmNodeHandler1, self).__init__()
        self.lat_lon = None
        self.inNode= False
        self.validNode = False
        self.searchPlaceValues = ('city', 'town', 'village')
        self.searchKeys = ('name', 'place', 'population')
        self.tags = None
        self.population = int(population)

    def startElement(self, name, attrs):
        if name == 'node':
            self.inNode = True
            self.lat_lon = [float(attrs['lat']), float(attrs['lon'])]
            self.tags = []
        if name == 'tag' and self.inNode and attrs['k'] in self.searchKeys:
            self.tags.append(attrs)
            if attrs['k'] == 'place' and attrs['v'] in self.searchPlaceValues:
                self.validNode = True

    def endElement(self, name):
        if name == 'node' and self.validNode:
            self.inNode = False
            self.validNode = False
            for tag in self.tags:
                if tag['k'] == 'population' and int(tag['v']) >= self.population:    # process only relevant info
                    print(self)
                    break

    def __str__(self):
        r = []
        for tag in self.tags:
            r.append(f'{tag["k"]}={tag["v"]}')
        return f'{self.lat_lon[0]}:{self.lat_lon[1]} {", ".join(r)}'

fname = r'c:\Usr\Maps\Test\3Rivieres'

parser = xml.sax.make_parser()
try:
    wayHandler = OsmWayHandler()
    parser.setContentHandler(wayHandler)
    parser.parse(open(fname + '.xml', 'r'))

    print(wayHandler.result)

    mapHandler = OsmMapHandler(wayHandler.result)
    parser.setContentHandler(mapHandler)
    parser.parse(open(fname + '.osm', 'r'))

    nodeHandler = OsmNodeHandler(mapHandler.result)
    parser.setContentHandler(nodeHandler)
    parser.parse(open(fname + '.osm', 'r'))
    print(nodeHandler.result)
except:
    pass

nodeHandler = OsmNodeHandler1()
parser.setContentHandler(nodeHandler)
parser.parse(open(r'c:\Usr\Maps\Osm\mauritius-latest.osm', 'r', encoding='utf-8'))
