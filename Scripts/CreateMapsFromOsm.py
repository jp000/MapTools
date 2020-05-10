# coding=utf-8

import os
import re
import shlex
import shutil
import subprocess
from datetime import datetime
from time import sleep
from os import path
import random
from urllib.parse import quote
import requests

# http://garmin.opentopomap.org/
# http://garmin.openstreetmap.nl/
# https://extract.bbbike.org/?lang=en
# https://download.geofabrik.de/
# https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
# https://www.alltrails.com/fr/
# http://geojson.io
# https://inkatlas.com
# https://www.traildino.com/

servers = (r'http://overpass.osm.ch/api/interpreter',
           r'http://overpass.openstreetmap.fr/api/interpreter',
           r'https://z.overpass-api.de/api/interpreter',
           r'https://lz4.overpass-api.de/api/interpreter',
           r'https://overpass.kumi.systems/api/interpreter',
           r'https://overpass.nchc.org.tw',
           )

root = r'C:\Usr\Maps'
wgetExe = r'C:\usr\bin\wget.exe'
dnldDir = os.path.join(root, 'Osm')
StyleDir = os.path.join(root, 'MapTools\Styles')
outDir = os.path.join(root, 'output')
mkgmapJar = os.path.join(root, 'mkgmap\mkgmap.jar')
splitterJar = os.path.join(root, 'splitter\splitter.jar')
options = os.path.join(StyleDir, 'config.cfg')
#javaOptions = '-Xmx4000m -Dlog.config="' + os.path.join(root, 'logging.opt') + '"'
javaOptions = '-Xmx4000m'
age = 21

if not os.path.exists(dnldDir):
    os.makedirs(dnldDir)


def fileAge(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 500:
        return 36500
    return (datetime.now() - datetime.fromtimestamp(path.getmtime(file_path))).days


def doOverpass(outputfilename, query, server=servers[1], bForce=False, bbox=None):
    if not bForce and fileAge(outputfilename) < age:
        print(f'File already OK {outputfilename}')
        return True
    tmp = os.path.join(os.path.dirname(outputfilename), 'Tmp.dat')
    if bbox is None:
        # data = f'data=[out:xml][timeout:600][maxsize:1073741824];{query}'
        data = f'data=[out:xml][timeout:900][maxsize:2147483648];{quote(query)}'
    else:
        # data=[bbox];node[amenity=post_box];out body;&bbox=6.4380,43.6490,7.5696,46.375068 (w,s,e,n)
        data = f'data=[out:xml][timeout:900][maxsize: 2147483648][bbox];{quote(query)}&bbox={bbox}'
    
    with open(tmp, 'w', encoding='utf-8') as fp:
        fp.writelines(data)
        print(f'Created {tmp}')
        print(f'{data}')
        
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


def doOverpassReq(outputfilename, query, server=servers[1], bForce=False, bbox=None):
    if not bForce and fileAge(outputfilename) < age:
        print(f'File already OK {outputfilename}')
        return True

    if bbox is None:
        p = {'data': f'[out:xml][timeout:900][maxsize:2147483648];{query}'}
    else:
        p = {'data': f'[out:xml][timeout:900][maxsize:2147483648][bbox];{query}',
             'bbox': bbox}
    with requests.get(server, params=p) as response:
        if response.status_code != 200:
            print(f'error: {response.reason} server:{server}')
            return False

        with open(outputfilename, 'wt', encoding='utf-8') as fp:
            fp.write(response.text)
            print(f'Created {outputfilename} server:{server}')
        return True


def downloadFile(outputfilename, remoteFilename, bForce):
    if not bForce and fileAge(outputfilename) < age:
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
    typeFile = f'"{typeFile}"' if typeFile is not None else ''

    cmd = fr'java {javaOptions} -jar "{javaJar}" -c "{options}" {route} --style-file="{styleDir}"  {mapName} --description="{mapDescription}" --output-dir="{outputDir}" {inputfilename} {typeFile}'

    return executeJava(cmd, mapDescription, outputDir)


def mkgmapTest(inputfilename,
           javaJar=mkgmapJar,
           mapId=0,
           mapDescription=None,
           hasRoute=True,
           outputDir=outDir):
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
            mapDescription = name

        if type(inputfilename) is list or type(inputfilename) is tuple:
            inputfilename = f' '.join([f'"{x}"' for x in inputfilename])
        else:
            inputfilename = f'"{inputfilename}"'
        mapName = f'--mapname={mapId} '
        
    route = '--route ' if hasRoute else ''

    cmd = fr'java {javaOptions} -jar "{javaJar}" -c "{options}" {route} {mapName} --description="{mapDescription}" --output-dir="{outputDir}" {inputfilename}'

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
        if r[0] is not None:
            print(f'Failed stdout:\n{r[0].decode("latin-1")}')
        if r[1] is not None:
            print(f'Failed stderr:\n{r[1].decode("latin-1")}')
        return None


def mkgsplit(inputfilename,
             javaJar=splitterJar,
             outputDir=outDir,
             description='JP Map',
             mapId=43600000,
             maxNodes=2400000):
    if mapId == 46600000:  # special for thailand
        maxNodes = 1600000
    cmd = fr'java  {javaOptions} -jar "{javaJar}" --max-nodes={maxNodes} --mapid={mapId} --description={description} --output-dir="{outputDir}" "{inputfilename}"'
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


def FindLastMapId(file):
    pattern = re.compile(r'mapname: (\d+)')
    with open(file, 'r') as fp:
        data = fp.read()
    matches = pattern.findall(data)
    return int(matches[-1])


def cleanup(root=outDir):
    import re
    pattern = re.compile('E10.+\.img$|E20.+\.img$|\.log$', re.IGNORECASE)
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


def ProcessGeoFabrik(urlRoot, osmFile, startId, styleName):
    _startId = lastId = startId
    if type(osmFile) is not list and type(osmFile) is not tuple:
        osmFile = (osmFile,)
    for _osmfile in osmFile:
        m = re.split('-latest', _osmfile)
        mapname = styleName + '_' + m[0]
        osmpath = os.path.join(dnldDir, _osmfile)
        template = None
        if downloadFile(osmpath, urlRoot + _osmfile, bForce=False):
            template = mkgsplit(osmpath, description=mapname, mapId=startId, maxNodes=1900000)

            if template is not None:
                lastId = FindLastMapId(template)
                mkgmap(template, styleDir=os.path.join(StyleDir, styleName),
                       typeFile=os.path.join(StyleDir, styleName + '.typ'), mapDescription=mapname)
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
        (0, 44444000, 'https://download.geofabrik.de/europe/', 'alps-latest.osm.pbf'),
        (0, 46100000, 'https://download.geofabrik.de/australia-oceania/', 'australia-latest.osm.pbf'),
        (0, 46400000, 'https://download.geofabrik.de/australia-oceania/', 'new-zealand-latest.osm.pbf'),
        (0, 46600000, 'https://download.geofabrik.de/asia/', 'thailand-latest.osm.pbf'),
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
        (0, 43300000, 'https://download.geofabrik.de/europe/france/', (#'franche-comte-latest.osm.pbf',
                                                                       #'nord-pas-de-calais-latest.osm.pbf',
                                                                       'provence-alpes-cote-d-azur-latest.osm.pbf',
                                                                       )),
        (0, 41000000, 'https://download.geofabrik.de/north-america/', ('us-midwest-latest.osm.pbf',
                                                                       'us-northeast-latest.osm.pbf',
                                                                       'us-pacific-latest.osm.pbf',
                                                                       'us-south-latest.osm.pbf',
                                                                       'us-west-latest.osm.pbf'
                                                                       )),
    ]

    if True:
        lastId, startId = 0, 0
        for entry in lst:
            if entry[0] != 0:
                lastId, startId = ProcessGeoFabrik(entry[2], entry[3], entry[1], 'E20x')
                print(f'from {startId} to {lastId} {entry[3]}')

    if False:
        lastId, startId = 0, 0
        for entry in lst:
            if entry[0] != 0:
                lastId, startId = ProcessGeoFabrik(entry[2], entry[3], entry[1] + 9000, 'E10')
                print(f'from {startId} to {lastId} {entry[3]}')


def make_Bbox(nbr, minLat=-90.0, minLon=-180.0, maxLat=90.0, maxLon=180.0):
    deltaLat, deltaLon = (maxLat - minLat) / nbr, (maxLon - minLon) / nbr
    nodes = []
    lon = minLon
    for y in range(nbr):
        lat = minLat
        for x in range(nbr):
            # swne
            nodes.append(f'{lat:.4f},{lon:.4f},{lat + deltaLat:.4f},{lon + deltaLon:.4f}')
            lat += deltaLat
        lon = lon + deltaLon
    return nodes


def swapNode(nodeStr):
    c = nodeStr.split(',')
    return f'{c[1]},{c[0]},{c[3]},{c[2]}'


def processWithBbox(nbr, query, minLat, minLon, maxLat, maxLon, outputName, startIndex, server):
    _outputnames = []
    nodes = make_Bbox(nbr, minLat, minLon, maxLat, maxLon)
    filenameIndex = startIndex
    for i in range(0, len(nodes)):
        n = os.path.join(dnldDir, f'{outputName}{i + startIndex}.osm')
        filenameIndex += 1
        if doOverpassReq(n, query, server=server, bbox=swapNode(nodes[i]), bForce=False):
            _outputnames.append(n)
            sleep(10.0)
    return _outputnames, filenameIndex

def getLinesFormGeojson(filename):
    from types import SimpleNamespace as Namespace
    import json
    lines = []
    geoJson = json.load(open(filename, 'r', encoding='utf-8'), object_hook=lambda d: Namespace(**d))
    for feature in geoJson.features:
        if feature.geometry.type == 'LineString':
            for coordinates in feature.geometry.coordinates:
                lines.append(f'{coordinates[1]:.4f},{coordinates[0]:.4f}')
            continue
        if feature.geometry.type == 'MultiLineString':
            for coordinates in feature.geometry.coordinates:
                for coordinate in coordinates:
                    lines.append(f'{coordinate[1]:.4f},{coordinate[0]:.4f}')
            continue

    return ','.join(lines)

if __name__ == '__main__':
    sty, typ = os.path.join(StyleDir, 'e20x'), os.path.join(StyleDir, 'e20x.typ')

    # q = 'is_in(46.77779,7.16022)->.a;area.a[boundary=administrative][admin_level=6];(node(area););( ._;<;<<;);'
    # doOverpass(r'.\Marly.osm', query=q)
    # mkgmap(r'.\Marly.osm', hasRoute=True, styleDir=r'\Usr\Maps\Styles\e20x', typeFile=r'\Usr\Maps\Styles\e20x.typ', mapId=94100000)
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
    if False:
        outputName = 'GR5_2704286'
        osm = os.path.join(dnldDir, f'{outputName}.osm')
        q1 = """rel(2704286);(
            way(r);node(w);node(around:2000);<;
            );out body;"""
        doOverpass(osm, query=q1, server=servers[2], bForce=True)
        template = mkgsplit(osm, description=f'{outputName}', mapId=43309000)
        if template is not None:
            lastId = FindLastMapId(template)
            mkgmap(template, mapDescription=f'E20_{outputName}', hasRoute=True, styleDir=sty, typeFile=typ)

    if True:
        outputName = 'Freiburger_Voralpenweg'
        osm = os.path.join(dnldDir, f'{outputName}.osm')
        l = getLinesFormGeojson(r'c:\Usr\Maps\Poi\GPX\Freiburger_Voralpenweg.geojson')
        q1 = f'(node(around:300,{l});' \
             '<;);out body;'
        doOverpass(osm, query=q1, server=servers[0], bForce=True)
        template = mkgsplit(osm, description=f'{outputName}', mapId=43309000)
        if template is not None:
            lastId = FindLastMapId(template)
            mkgmap(template, mapDescription=f'E20_{outputName}', hasRoute=True,
                   styleDir=os.path.join(StyleDir, r'e20x'), typeFile=os.path.join(StyleDir, r'e20x.typ'))

    if False:
        q1 = 'node(-58.0,-180.0,0.0,180.0)[population](if: t["population"] >= 1000000);out body;'
        q2 = 'node(0.0,-180.0,40.0,180.0)[population](if: t["population"] >= 1000000);out body;'
        q3 = 'node(40.0,-180.0,83.0,180.0)[population](if: t["population"] >= 1000000);out body;'
        doOverpass('.\Cities1.osm', query=q1)
        doOverpass('.\Cities2.osm', query=q2)
        doOverpass('.\Cities3.osm', query=q3)
        mkgmap(('.\Cities1.osm', '.\Cities2.osm', '.\Cities3.osm'), hasRoute=False, styleDir=sty, typeFile=typ,
               mapId=99990000, mapDescription='E20_Cities')

    if False:
        outputName = 'Cities'
        # q1 = 'node(0.0,-180.0,   90.0  ,0.0)[place~"city|town|village"][population~"[0-9]+"](if: t["population"] >= 5000000);out body;'
        q1 = 'node(0.0,-180.0,   90.0  ,0.0)[place~"city|town|village"](if: t["population"] >= 5000000);out body;'
        q2 = 'node(0.0,0.0,      90.0,180.0)[place~"city|town|village"][population~"^[0-9]+$"](if: t["population"] >= 5000000);out body;'
        q3 = 'node(-90.0,-180.0, 0.0,   0.0)[place~"city|town|village"][population~"^[0-9]+$"](if: t["population"] >= 5000000);out body;'
        q4 = 'node(-90.0,0.0,    0.0, 180.0)[place~"city|town|village"][population~"^[0-9]+$"](if: t["population"] >= 5000000);out body;'
        doOverpass(f'.\{outputName}1.osm', query=q1, server=servers[1])
        doOverpass(f'.\{outputName}2.osm', query=q2, server=servers[1])
        doOverpass(f'.\{outputName}3.osm', query=q3, server=servers[1])
        doOverpass(f'.\{outputName}4.osm', query=q4, server=servers[1])
        mkgmapTest((f'.\{outputName}1.osm', f'.\{outputName}2.osm', f'.\{outputName}3.osm', f'.\{outputName}4.osm'),
                   hasRoute=False, mapId=99990000, mapDescription=f'E20_{outputName}')

    if False:
        outputName = 'LargeCity'
        queries = []
        bbox = []
        queries.extend(nodeBbox(2, '[place=city];out body;'))
        bbox.extend(atBbox(2))
        queries.extend(nodeBbox(2, '[place=town];out body;'))
        bbox.extend(atBbox(2))
        queries.extend(nodeBbox(3, '[place=village](if: number(t["population"]) >= 5000);out body;', maxLon=0))
        bbox.extend(atBbox(3, maxLon=0))
        queries.extend(nodeBbox(6, '[place=village](if: number(t["population"]) >= 5000);out body;', minLon=0))
        bbox.extend(atBbox(6, minLon=0))
        osmFiles = []
        fail = False
        for i in range(len(queries)):
            osm = os.path.join(dnldDir, f'{outputName}{i + 1}.osm')
            osmFiles.append(osm)
            print(f'{i + 1} / {len(queries)}')
            if not doOverpass(osm, query=queries[i], server=servers[random.choice([1, 2, 3])], bbox=bbox[i]):
                fail = True
                # break
        if not fail:
            mkgmapTest(osmFiles, hasRoute=False, mapId=99990000, mapDescription=f'E20_{outputName}')

    if False:
        outputName = 'X'
        outputnames, idx = processWithBbox(4,
                                           '('
                                           'node[place=city](if: number(t["population"]) >= 1000000);'
                                           'node[place=town](if: number(t["population"]) >= 1000000);'
                                           'node[place=village](if: number(t["population"]) >= 1000000);'
                                           ');out body;',
                                           minLat=-90.0, minLon=-180.0, maxLat=90.0, maxLon=180.0,
                                           outputName='X', startIndex=1, server=servers[3])
        mkgmap(outputnames, hasRoute=False, styleDir=sty, typeFile=typ, mapId=99990000,
               mapDescription=f'E20_{outputName}')

    if False:
        outputName = 'Fribourg'
        osm = os.path.join(dnldDir, f'{outputName}.osm')
        q1 = """
            area["ISO3166-2"="CH-FR"];node(area);
            ( ._;<;<<;);
            out body;
        """
        doOverpass(osm, query=q1)
        template = mkgsplit(osm, description=f'{outputName}', mapId=91000000)
        if template is not None:
            lastId = FindLastMapId(template)
            mkgmap(template, styleDir=sty, mapDescription=f'E20_{outputName}', typeFile=typ)

    if False:
        q1 = '(area["name:en"="Republic of Crimea"][type=boundary][boundary=administrative][admin_level=4]["addr:country"="RU"];)->.x;(node(area.x););(._;<;<<;);out body;'
        doOverpass('.\Crimee.osm', query=q1)
        template = mkgsplit(r'.\Crimee.osm', description='Crimee', mapId=91000000)
        if template is not None:
            lastId = FindLastMapId(template)
            mkgmap(template, styleDir=sty, mapDescription='E20_Crimee', typeFile=typ)

    if False:
        q1 = '''area["ISO3166-1"="CH"][admin_level=2] -> .ch;
            node[place=hamlet](area.ch) -> .p1;
            node[place=village](area.ch) -> .p2;
            node[place=city](area.ch) -> .p3;
            node[place=town](area.ch) -> .p4;
            node[place=isolated_dwelling](area.ch) -> .p5;
            node[amenity=toilets](area.ch) -> .a1;
            rel[type=route][route~"hiking|foot"](area.ch) -> .r1;
            rel[type=route][route~"bicycle|mtb"](area.ch) -> .r2;
            (
            .p1;.p2;.p3;.p4;.p5;.a1;.r1;.r2;
            );
            ( ._;>;>>;<;); 
            out body;
        '''
        doOverpass('.\CHTest.osm', query=q1, server=servers[3])
        template = mkgsplit(r'.\CHTest.osm', description='CHTest', mapId=10000000)
        if template is not None:
            lastId = FindLastMapId(template)
            mkgmap(template, mapDescription='E10_CHTest', hasRoute=False)

    if False:
        q1 = '''(
            area[name="Fribourg/Freiburg"][boundary=administrative][admin_level=4]; 
            area[name="District de la Broye-Vully"][type=boundary][boundary=administrative][admin_level=6]; 
            area[name="District de la Riviera-Pays-d’Enhaut"][type=boundary][boundary=administrative][admin_level=6]; 
            area[name="District d'Aigle"][type=boundary][boundary=administrative][admin_level=6];
            area[name="Monthey"][type=boundary][boundary=administrative][admin_level=6];
            area[name="Saint-Maurice"][type=boundary][boundary=administrative][admin_level=6];
            area[name="Verwaltungskreis Obersimmental-Saanen"][type=boundary][boundary=administrative][admin_level=6];
            )->.x;
            (
            node(area.x);  
            );
            ( ._;<;<<;); 
            out body; 
        '''
        doOverpass('.\Fribourg.osm', query=q1, server=servers[3])
        template = mkgsplit(r'.\Fribourg.osm', description='CHTest', mapId=10000000)
        if template is not None:
            lastId = FindLastMapId(template)
            mkgmap(template, mapDescription='E10_Fribourg', hasRoute=False)

    if False:
        # https://extract.bbbike.org?sw_lng=13.215&sw_lat=41.951&ne_lng=19.964&ne_lat=46.231&format=osm.pbf&coords=14.962%2C43.213%7C17.114%2C42.102%7C19.86%2C41.951%7C19.964%2C42.825%7C17.575%2C44.192%7C14.373%2C46.231%7C13.215%2C45.478%7C13.979%2C44.309&city=Yougoslavie&lang=en
        template = mkgsplit(os.path.join(dnldDir, 'planet_15.731_43.069_8e27d44d.osm.pbf'), description='Yougoslavie',
                            mapId=93850000)
        if template is not None:
            mkgmap(template, styleDir=sty, typeFile=typ, mapDescription='E20_Yougoslavie')

    GeoFabrik()
    cleanup()
