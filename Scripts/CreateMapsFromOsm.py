# coding=utf-8

import os
import re
import shlex
import shutil
import subprocess
from datetime import datetime
from os import path

# http://garmin.opentopomap.org/
# http://garmin.openstreetmap.nl/
# https://extract.bbbike.org/?lang=en
# https://download.geofabrik.de/

servers = (r'http://overpass-api.de/api/interpreter',
           r'http://overpass.openstreetmap.fr/api/interpreter',
           r'https://lz4.overpass-api.de/api/interpreter',
           r'http://overpass.osm.ch/api/interpreter',
           r'https://overpass.kumi.systems/api/interpreter',
           r'https://z.overpass-api.de/api/interpreter'
           )

dnldDir1 = r'C:\Users\JPE\Downloads'
dnldDir = r'C:\Usr\Maps\Osm'
StyleDir = r'c:\Usr\Maps\MapTools\Styles'
outDir = r'C:\Usr\Maps\output'
mkgmapJar = r'C:\Usr\Maps\mkgmap\mkgmap.jar'
splitterJar = r'C:\Usr\Maps\splitter\splitter.jar'
wgetExe = r'C:/usr/bin/wget.exe'

if not os.path.exists(dnldDir):
    os.makedirs(dnldDir)


def fileAge(file_path):
    if not os.path.exists(file_path):
        return 36500
    return (datetime.now() - datetime.fromtimestamp(path.getmtime(file_path))).days


def doOverpass(outputfilename, query, server=servers[2], bbox=None):
    tmp = os.path.join(os.path.dirname(outputfilename), 'Tmp.dat')
    if bbox is None:
        #data = f'data=[out:xml][timeout:600][maxsize:1073741824];{query}'
        data = f'data=[out:xml][timeout:600][maxsize:2147483648];{query}'
    else:
        # data=[bbox];node[amenity=post_box];out body;&bbox=6.4380,43.6490,7.5696,46.375068 (w,s,e,n)
        data = f'data=[out:xml][timeout:600][maxsize:1073741824][bbox];{query}&bbox={bbox}'

    with open(tmp, 'w', encoding='utf-8') as fp:
        fp.writelines(data)
        print(f'Created {tmp}')
    cmd = fr'"{wgetExe}" -O "{outputfilename}" --post-file="{tmp}" {server}'
    print(f'Execute {cmd}')
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        print(f'Created {outputfilename}')
        return True
    else:
        print(f'Failed\n{r[1].decode("latin-1")}')
        return False


def downloadFile(outputfilename, remoteFilename):
    if fileAge(outputfilename) < 21:
        print(f'File already OK {outputfilename}')
        return True
    cmd = fr'"{wgetExe}" -O "{outputfilename}" "{remoteFilename}"'
    print(f'Execute {cmd}')
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        print(f'Created {outputfilename}')
        return True
    else:
        print(f'Failed\n{r[1].decode("latin-1")}')
        return False


def mkgmap(inputfilename,
           javaJar=mkgmapJar,
           styleDir=os.path.join(StyleDir, r'e10'),
           typeFile=os.path.join(StyleDir, r'e10.typ'),
           mapId=0,
           mapDescription=None,
           hasRoute=True,
           outputDir=outDir):
    poiExclude = '--poi-excl-index=0x2a13,0x2b05,0x2b06,0x2c0d,0x2e0c,0x6619,0x2800'
    styleName = os.path.split(styleDir)[-1]
    if type(inputfilename) is list or type(inputfilename) is tuple:
        name, ext = os.path.splitext(os.path.basename(inputfilename[0]))
    else:
        name, ext = os.path.splitext(os.path.basename(inputfilename))
    if ext == '.args':
        inputfilename = f'-c "{inputfilename}"'
        mapName = ''
        if mapDescription is None:
            mapDescription = 'Noname'
    else:
        if mapDescription is None:
            mapDescription = name + '_' + styleName

        if type(inputfilename) is list or type(inputfilename) is tuple:
            inputfilename = f' '.join([f'"{x}"' for x in inputfilename])
        else:
            inputfilename = f'"{inputfilename}"'
        mapName = f'--mapname={mapId} '

    route = '--route ' if hasRoute else ''
    if typeFile is None or typeFile == '':
        typeFile = ''
    else:
        typeFile = f'"{typeFile}"'

    cmd = fr'java -Xmx4000m -jar "{javaJar}" --gmapsupp --latin1 --index --add-pois-to-areas {poiExclude} --ignore-fixme-values {route} --style-file="{styleDir}" --family-id=1000 --product-id=1 {mapName} --description="{mapDescription}" --output-dir="{outputDir}" {inputfilename} {typeFile}'

    return executeJava(cmd, mapDescription, outputDir)


def executeJava(cmd, mapName, outputDir):
    print(f'Execute {cmd}')
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        resultFilename = os.path.abspath(os.path.join(outputDir, mapName + '.img'))
        print(f'Created {resultFilename} from {os.path.join(outputDir, "gmapsupp.img")}')
        shutil.copyfile(os.path.join(outputDir, 'gmapsupp.img'), resultFilename)
        return resultFilename
    else:
        print(f'Failed\n{r[1].decode("latin-1")}')
        return None


def mkgsplit(inputfilename,
             javaJar=splitterJar,
             outputDir=outDir,
             description='JP Map',
             mapId=43600000):
    cmd = fr'java -Xmx4000m -jar "{javaJar}" --max-nodes=2400000 --mapid={mapId} --description={description} --output-dir="{outputDir}" "{inputfilename}"'
    print(f'Execute {cmd}')
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        print(f'Created {os.path.join(outputDir, "template.args")}')
        return os.path.join(outputDir, 'template.args')
    else:
        print(f'Failed\n{r[1].decode("latin-1")}')
        return None


def mkMap(osm, myId, query,
          styleDir=os.path.join(StyleDir, r'e10'),
          typeFile=os.path.join(StyleDir, r'e10.typ')):
    doOverpass(osm, query)
    return mkgmap(osm, styleDir=styleDir, typeFile=typeFile, mapId=myId)


# def Replace(data, startId):
#     global newid
#
#     def _replace(m):
#         global newid
#         s = 'mapname: {:08d}'.format(newid)
#         newid += 1
#         return s
#
#     pattern = re.compile(r'mapname: \d+')
#     newid = startId
#     return pattern.sub(lambda m: _replace(m.group(0)), data), newid

def FindLastMapId(file):
    pattern = re.compile(r'mapname: (\d+)')
    with open(file, 'r') as fp:
        data = fp.read()
    matches = pattern.findall(data)
    return int(matches[-1])


# def updateMapId(file, myId):
#     with open(file, 'r+') as fp:
#         data = fp.read()
#         d = Replace(data, myId)
#         fp.seek(0, 0)
#         fp.write(d[0])
#     return d[1]


def cleanup(root=outDir):
    import re
    pattern = re.compile('E10.+\.img$|E20.+\.img$', re.IGNORECASE)
    r = []
    for dirpath, dirnames, filenames in os.walk(root):
        del dirnames[:]
        for filename in filenames:
            if pattern.search(filename):
                continue
            name = os.path.join(dirpath, filename)
            if os.path.isfile(name):
                r.append(name)
    for f in r:
        os.unlink(f)


def ProcessGeoFabrik(urlRoot, osmFile, startId):
    _startId = lastId = startId
    if type(osmFile) is not list and type(osmFile) is not tuple:
        osmFile = (osmFile,)
    for _osmfile in osmFile:
        m = re.split('-latest', _osmfile)
        mapname = m[0]
        osmpath = os.path.join(dnldDir, _osmfile)
        template = None
        if downloadFile(osmpath, urlRoot + _osmfile):
            template = mkgsplit(osmpath, description=mapname, mapId=startId)

            if template is not None:
                lastId = FindLastMapId(template)
                mkgmap(template, styleDir=os.path.join(StyleDir, 'e20x'),
                       typeFile=os.path.join(StyleDir, 'e20x.typ'), mapDescription='E20_' + mapname)
            startId = lastId + 1
    return lastId, _startId


def GeoFabrik():
    lst = [
        (0, 42300000, 'https://download.geofabrik.de/africa/', 'mauritius-latest.osm.pbf'),
        (0, 42610000, 'https://download.geofabrik.de/africa/', 'madagascar-latest.osm.pbf'),
        (0, 43100000, 'https://download.geofabrik.de/europe/', 'netherlands-latest.osm.pbf'),
        (0, 43200000, 'https://download.geofabrik.de/europe/', 'belgium-latest.osm.pbf'),
        (0, 43300000, 'https://download.geofabrik.de/europe/', 'france-latest.osm.pbf'),
        (0, 43400000, 'https://download.geofabrik.de/europe/', 'spain-latest.osm.pbf'),
        (0, 43570000, 'https://download.geofabrik.de/europe/', 'cyprus-latest.osm.pbf'),
        (0, 43900000, 'https://download.geofabrik.de/europe/', 'italy-latest.osm.pbf'),
        (0, 44100000, 'https://download.geofabrik.de/europe/', 'switzerland-latest.osm.pbf'),
        (0, 44300000, 'https://download.geofabrik.de/europe/', 'austria-latest.osm.pbf'),
        (0, 44400000, 'https://download.geofabrik.de/europe/', 'great-britain-latest.osm.pbf'),
        (0, 44900000, 'https://download.geofabrik.de/europe/', 'germany-latest.osm.pbf'),
        (0, 46100000, 'https://download.geofabrik.de/australia-oceania/', 'australia-latest.osm.pbf'),
        (0, 46400000, 'https://download.geofabrik.de/australia-oceania/', 'new-zealand-latest.osm.pbf'),
        (0, 00000000, 'https://download.geofabrik.de/xxx/', 'xxx.pbf'),

        (0, 43300000, 'https://download.geofabrik.de/europe/france/', ('franche-comte-latest.osm.pbf',
                                                                       'haute-normandie-latest.osm.pbf',
                                                                       'basse-normandie-latest.osm.pbf',
                                                                       'ile-de-france-latest.osm.pbf',
                                                                       'nord-pas-de-calais-latest.osm.pbf',
                                                                       'picardie-latest.osm.pbf',
                                                                       'provence-alpes-cote-d-azur-latest.osm.pbf',
                                                                       'rhone-alpes-latest.osm.pbf',
                                                                       'pays-de-la-loire-latest.osm.pbf',
                                                                       'bretagne-latest.osm.pbf',
                                                                       'alsace-latest.osm.pbf',
                                                                       'aquitaine-latest.osm.pbf',
                                                                       'auvergne-latest.osm.pbf',
                                                                       'bourgogne-latest.osm.pbf',
                                                                       'centre-latest.osm.pbf',
                                                                       'champagne-ardenne-latest.osm.pbf',
                                                                       'languedoc-roussillon-latest.osm.pbf',
                                                                       'limousin-latest.osm.pbf',
                                                                       'lorraine-latest.osm.pbf',
                                                                       'midi-pyrenees-latest.osm.pbf',
                                                                       'poitou-charentes-latest.osm.pbf',
                                                                       'corse-latest.osm.pbf',
                                                                       )),
        (0, 43300000, 'https://download.geofabrik.de/europe/france/', ('franche-comte-latest.osm.pbf',
                                                                       'nord-pas-de-calais-latest.osm.pbf',
                                                                       )),
    ]

    lastId, startId = 0, 0
    for entry in lst:
        if entry[0] != 0:
            lastId, startId = ProcessGeoFabrik(entry[2], entry[3], entry[1])
            print(f'from {startId} to {lastId} {entry[3]}')


if __name__ == '__main__':

    #q = 'is_in(46.77779,7.16022)->.a;area.a[boundary=administrative][admin_level=6];(node(area););( ._;<;<<;);'
    #doOverpass(r'.\Marly.osm', query=q)
    #mkgmap(r'.\Marly.osm', hasRoute=True, styleDir=r'\Usr\Maps\Styles\e20x', typeFile=r'\Usr\Maps\Styles\e20x.typ', mapId=94100000)
    #    mkgmap(r'.\Marly.osm', styleDir=r'\Usr\Maps\Styles\e20', typeFile=r'\Usr\Maps\Styles\e20.typ')
    #    files = []
    #    files.append(mkMap(r'.\CH-AR.osm', 43600001, query=r'area["ISO3166-2"="CH-AR"];(node(area););( ._;<;<<;);'))
    #    files.append(mkMap(r'.\CH-AI.osm', 43600002, query=r'area["ISO3166-2"="CH-AI"];(node(area););( ._;<;<<;);'))
    #    files.append(mkMap(r'.\CH-SG.osm', 43600003, query=r'area["ISO3166-2"="CH-SG"];(node(area););( ._;<;<<;);'))
    #    files.append(mkMap(r'.\CH-FR.osm', 43600004, query=r'area["ISO3166-2"="CH-FR"];(node(area););( ._;<;<<;);'))

    #    q = 'rel["name"~"GR 5",i][type=route][route~"hiking|foot"]{0};( way(r){0};node(w){0};node(around:3000){0};<; );'
    #    doOverpass(r'.\GR5Sud.osm', query=q.format('(43.6490,6.4380,46.375068,7.5696)'), server=servers[0])
    #    mkgmap(r'.\GR5Sud.osm', styleDir=r'\Usr\Maps\Styles\e20x', typeFile=r'\Usr\Maps\Styles\e20x.typ')

    #    q = '(node{0};<;);out;'
    #    doOverpass(r'.\GR5Sud.osm', query=q.format('(46.7,7.1,46.8,7.2)'), server=servers[0])
    # doOverpass(r'.\GR5Sud.osm', query=q.format('()'), server=servers[0], bbox='6.4,43.6,6.5,43.7')
    #    template = mkgsplit('.\GR5Sud.osm')
    #    if template is not None:
    #        startId = updateMapId(template, 43500001)
    #        mkgmap(template, styleDir=os.path.join(StyleDir, 'e20x'), typeFile=os.path.join(StyleDir, 'e20x.typ'), mapDescription='GR5Sud_E20')

    if True:
        q1 = 'node(-58.0,-180.0,0.0,180.0)[place~"city|town"](if: t["population"] >= 4000);out body;'
        q2 = 'node(0.0,-180.0,40.0,180.0)[place~"city|town"](if: t["population"] >= 4000);out body;'
        q3 = 'node(40.0,-180.0,83.0,180.0)[place~"city|town"](if: t["population"] >= 4000);out body;'
        doOverpass('.\Villes1.osm', query=q1)
        doOverpass('.\Villes2.osm', query=q2)
        doOverpass('.\Villes3.osm', query=q3)
        mkgmap(('.\Villes1.osm', '.\Villes2.osm', '.\Villes3.osm'), hasRoute=False, styleDir=r'\Usr\Maps\MapTools\Styles\E20x', typeFile=r'\Usr\Maps\MapTools\Styles\E20x.typ', mapId=99990000, mapDescription='E20_Villes')

    if False:
        # https://extract.bbbike.org?sw_lng=13.215&sw_lat=41.951&ne_lng=19.964&ne_lat=46.231&format=osm.pbf&coords=14.962%2C43.213%7C17.114%2C42.102%7C19.86%2C41.951%7C19.964%2C42.825%7C17.575%2C44.192%7C14.373%2C46.231%7C13.215%2C45.478%7C13.979%2C44.309&city=Yougoslavie&lang=en
        template = mkgsplit(os.path.join(dnldDir1, 'planet_15.731_43.069_8e27d44d.osm.pbf'),description='Yougoslavie',
             mapId=93850000)
        if template is not None:
            mkgmap(template,
                   styleDir=os.path.join(StyleDir, 'e20x'), typeFile=os.path.join(StyleDir, 'e20x.typ'),
                   mapDescription='E20_Yougoslavie')

    GeoFabrik()
    cleanup()
