import lxml.sax

class OsmNodeHandler(lxml.sax.ContentHandler):
    def __init__(self, population=0):
        super(OsmNodeHandler, self).__init__()
        self.lat_lon = None
        self.inNode= False
        self.validNode = False
        self.searchPlaceValues = ('city', 'town', 'village')
        self.searchKeys = ('name', 'place', 'population')
        self.tags = None
        self.population = int(population)
        self.uri = None

    def startElementNS(self, name, qname, attrs):
        uri, localname = name
        self.uri = uri
        if localname == 'node':
            self.inNode = True
            self.lat_lon = [float(attrs[(uri,'lat')]), float(attrs[(uri,'lon')])]
            self.tags = []
        if localname == 'tag' and self.inNode and attrs[(uri,'k')] in self.searchKeys:
            self.tags.append(attrs)
            if attrs[(uri,'k')] == 'place' and attrs[(uri,'v')] in self.searchPlaceValues:
                self.validNode = True

    def endElementNS(self, name, qname):
        uri, localname = name
        if localname == 'node' and self.validNode:
            self.inNode = False
            self.validNode = False
            for tag in self.tags:
                if tag[(uri,'k')] == 'population' and int(tag[(uri,'v')]) >= self.population:    # process only relevant info
                    print(self)
                    break

    def __str__(self):
        r = []
        for tag in self.tags:
            r.append(f'{tag[(self.uri,"k")]}={tag[(self.uri,"v")]}')
        return f'{self.lat_lon[0]}:{self.lat_lon[1]} {", ".join(r)}'

tree = lxml.etree.parse(open(r'C:\Usr\Maps\Tmp\landes_1.osm', 'r', encoding='utf-8'))

nodeHandler = OsmNodeHandler(2000)
lxml.sax.saxify(tree, nodeHandler)