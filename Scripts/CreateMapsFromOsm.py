# coding=utf-8

import os, sys, stat
import re
import shlex
import shutil
import subprocess
from os import path
from datetime import datetime, timedelta

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
StyleDir = r'C:\Usr\Maps\Styles'
outDir = r'C:\Usr\Maps\output'
mkgmapJar = r'C:\Usr\Maps\mkgmap\mkgmap.jar'
splitterJar = r'C:\Usr\Maps\splitter\splitter.jar'
wgetExe = r'C:/usr/bin/wget.exe'

if not os.path.exists(dnldDir):
    os.makedirs(dnldDir)


#def fileOld(file_path):
#    if not os.path.exists(file_path):
#        return True
#    days_ago = datetime.now() - timedelta(weeks=4)
#    filetime = datetime.fromtimestamp(path.getctime(file_path))
#    return filetime < days_ago


def fileAge(file_path):
    if not os.path.exists(file_path):
        return 36500
    return (datetime.now() - datetime.fromtimestamp(path.getctime(file_path))).days


def doOverpass(outputfilename, query, server=servers[2], bbox=None):
    tmp = os.path.join(os.path.dirname(outputfilename), 'Tmp.dat')
    if bbox is None:
        data = 'data=[out:xml][timeout:600][maxsize:1073741824];{}'.format(query)
    else:
        # data=[bbox];node[amenity=post_box];out body;&bbox=6.4380,43.6490,7.5696,46.375068 (w,s,e,n)
        data = 'data=[out:xml][timeout:600][maxsize:1073741824][bbox];{}&bbox={}'.format(query, bbox)

    with open(tmp, 'w', encoding='utf-8') as fp:
        fp.writelines(data)
        print('Created {}'.format(tmp))
    cmd = r'"{3}" -O "{0}" --post-file="{1}" {2}'.format(outputfilename, tmp, server, wgetExe)
    print('Execute {}'.format(cmd))
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        print('Created {}'.format(outputfilename))
        return True
    else:
        print('Failed\n{}'.format(r[1].decode('latin-1')))
        return False


def downloadFile(outputfilename, remoteFilename):
    if fileAge(outputfilename) < 21:
        print('File already OK {}'.format(outputfilename))
        return True
    cmd = r'"{2}" -O "{0}" "{1}"'.format(outputfilename, remoteFilename, wgetExe)
    print('Execute {}'.format(cmd))
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        print('Created {}'.format(outputfilename))
        return True
    else:
        print('Failed\n{}'.format(r[1].decode('latin-1')))
        return False


def mkgmap(inputfilename,
           javaJar=mkgmapJar,
           styleDir=os.path.join(StyleDir, r'e10'),
           typeFile=os.path.join(StyleDir, r'e10.typ'),
           mapId=4360001,
           mapDescription=None,
           hasRoute=True,
           outputDir=outDir):
    poiExclude = '--poi-excl-index=0x2a13,0x2b05,0x2b06,0x2c0d,0x2e0c,0x6619,0x2800'
    styleName = os.path.split(styleDir)[-1]
    name, ext = os.path.splitext(os.path.basename(inputfilename))
    if ext == '.args':
        inputfilename = '-c "{}"'.format(inputfilename)
        mapName = ''
        if mapDescription is None:
            mapDescription = 'Noname'
    else:
        if mapDescription is None:
            mapDescription = name + '_' + styleName
        inputfilename = '"{}"'.format(inputfilename)
        mapName = '--mapname={} '.format(mapId)

    route = '--route ' if hasRoute else ''
    if typeFile is None or typeFile == '':
        typeFile = ''
    else:
        typeFile = '"{}"'.format(typeFile)

    cmd = r'java -Xmx4000m -jar "{0}" --gmapsupp --latin1 --index --add-pois-to-areas {8} --ignore-fixme-values {7}' \
          r' --style-file="{1}" --family-id=1000 --product-id=1 {2}' \
          r' --description="{3}" --output-dir="{4}" {5} {6}' \
        .format(javaJar, styleDir, mapName, mapDescription, outputDir, inputfilename, typeFile, route, poiExclude)

    return executeJava(cmd, mapDescription, outputDir)


def executeJava(cmd, mapName, outputDir):
    print('Execute {}'.format(cmd))
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        resultFilename = os.path.abspath(os.path.join(outputDir, mapName + '.img'))
        print('Created {} from {}'.format(resultFilename, os.path.join(outputDir, 'gmapsupp.img')))
        shutil.copyfile(os.path.join(outputDir, 'gmapsupp.img'), resultFilename)
        return resultFilename
    else:
        print('Failed\n{}'.format(r[1].decode('latin-1')))
        return None


def mkgsplit(inputfilename,
             javaJar=splitterJar,
             outputDir=outDir):
    cmd = r'java -Xmx4000m -jar "{0}" --output-dir="{1}" "{2}"'.format(javaJar, outputDir, inputfilename)
    print('Execute {}'.format(cmd))
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    if p.returncode == 0:
        print('Created {}'.format(os.path.join(outputDir, 'template.args')))
        return os.path.join(outputDir, 'template.args')
    else:
        print('Failed\n{}'.format(r[1].decode('latin-1')))
        return None


def mkMap(osm, myId, query,
          styleDir=os.path.join(StyleDir, r'e10'),
          typeFile=os.path.join(StyleDir, r'e10.typ')):
    doOverpass(osm, query)
    return mkgmap(osm, styleDir=styleDir, typeFile=typeFile, mapId=myId)


def Replace(data, startId):
    global newid

    def _replace(m):
        global newid
        s = 'mapname: {:08d}'.format(newid)
        newid += 1
        return s
    pattern = re.compile(r'mapname: \d+')
    newid = startId
    return pattern.sub(
        lambda m: _replace(m.group(0)), data), newid


def updateMapId(file, myId):
    with open(file, 'r+') as fp:
        data = fp.read()
        d = Replace(data, myId)
        fp.seek(0, 0)
        fp.write(d[0])
    return d[1]


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
    if type(osmFile) is list or type(osmFile) is tuple:
        pass
    else:
        osmFile = (osmFile,)
    for _osmfile in osmFile:
        m = re.split('-latest', _osmfile)
        mapname = m[0]
        osmpath = os.path.join(dnldDir, _osmfile)
        if downloadFile(osmpath, urlRoot + _osmfile):
            template = mkgsplit(osmpath)
            if template is not None:
                # startId = updateMapId(template, startId)
                # mkgmap(template, styleDir=os.path.join(StyleDir, 'e10'), typeFile=os.path.join(StyleDir, 'e10.typ'), mapDescription='E10_' + mapName)
                startId = updateMapId(template, startId)
                mkgmap(template, styleDir=os.path.join(StyleDir, 'e20x'),
                       typeFile=os.path.join(StyleDir, 'e20x.typ'), mapDescription='E20_' + mapname)
    return startId

if __name__ == '__main__':

    #    q = 'is_in(46.77779,7.16022)->.a;area.a[boundary=administrative][admin_level=6];(node(area););( ._;<;<<;);'
    #    doOverpass(r'.\Marly.osm', query=q)
    #    mkgmap(r'.\Marly.osm', hasRoute=False)
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
        urlRoot = 'https://download.geofabrik.de/europe/'
        startId = ProcessGeoFabrik(urlRoot, 'switzerland-latest.osm.pbf', 44100001)

    if False:
        urlRoot = 'https://download.geofabrik.de/europe/'
        startId = ProcessGeoFabrik(urlRoot, 'france-latest.osm.pbf', 43610001)

    if True:
        urlRoot = 'https://download.geofabrik.de/europe/italy/'
        osmFiles = ('nord-est-latest.osm.pbf',
            'nord-ovest-latest.osm.pbf',
            'centro-latest.osm.pbf')
        startId = ProcessGeoFabrik(urlRoot, osmFiles, 43900001)

    if False:
        # https://extract.bbbike.org?sw_lng=13.215&sw_lat=41.951&ne_lng=19.964&ne_lat=46.231&format=osm.pbf&coords=14.962%2C43.213%7C17.114%2C42.102%7C19.86%2C41.951%7C19.964%2C42.825%7C17.575%2C44.192%7C14.373%2C46.231%7C13.215%2C45.478%7C13.979%2C44.309&city=Yougoslavie&lang=en
        template = mkgsplit(os.path.join(dnldDir1, 'planet_15.138_43.277_e8b7a8d8.osm.pbf'))
        if template is not None:
            startId = updateMapId(template, 43700001)
            # mkgmap(template, styleDir=os.path.join(StyleDir, 'e10'), typeFile=os.path.join(StyleDir, 'e10.typ'), mapDescription='E10_Yougoslavie')
            # startId = updateMapId(template, startId)
            mkgmap(template, styleDir=os.path.join(StyleDir, 'e20x'), typeFile=os.path.join(StyleDir, 'e20x.typ'),
                   mapDescription='E20_Yougoslavie')

    if True:
        urlRoot = 'https://download.geofabrik.de/europe/france/'
        osmFiles = ('franche-comte-latest.osm.pbf',
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
                    'auvergne.html',
                    'bourgogne-latest.osm.pbf',
                    'centre-latest.osm.pbf',
                    'champagne-ardenne-latest.osm.pbf',
                    'languedoc-roussillon-latest.osm.pbf',
                    'limousin-latest.osm.pbf',
                    'lorraine-latest.osm.pbf',
                    'midi-pyrenees-latest.osm.pbf',
                    'poitou-charentes-latest.osm.pbf',
                    'corse-latest.osm.pbf',
                    )
        startId = ProcessGeoFabrik(urlRoot, osmFiles, 43300001)

    if False:
        urlRoot = 'https://download.geofabrik.de/europe/germany/'
        osmFiles = ('baden-wuerttemberg-latest.osm.pbf',
                    'bayern-latest.osm.pbf',
                    'https://download.geofabrik.de/europe/germany/saarland-latest.osm.pbf',
                    'https://download.geofabrik.de/europe/germany/rheinland-pfalz-latest.osm.pbf'
                    )
        startId = ProcessGeoFabrik(urlRoot, osmFiles, 4440001)
 
    if False:
        urlRoot = 'https://download.geofabrik.de/europe/'
        startId = ProcessGeoFabrik(urlRoot, 'austria-latest.osm.pbf', 44300001)
 
    if False:
        urlRoot = 'https://download.geofabrik.de/europe/'
        startId = ProcessGeoFabrik(urlRoot, 'cyprus-latest.osm.pbf', 43900001)

    if False:
        urlRoot = 'https://download.geofabrik.de/australia-oceania/'
        osmFiles = ('australia-latest.osm.pbf',
                    'new-zealand-latest.osm.pbf',
                    )
        startId = ProcessGeoFabrik(urlRoot, osmFiles, 46100001)

    cleanup()

# https://download.geofabrik.de/africa/madagascar-latest.osm.pbf
# https://download.geofabrik.de/africa/mauritius-latest.osm.pbf