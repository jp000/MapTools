# coding=utf-8
from __future__ import print_function

import requests


urlFmt = r'http://overpass-api.de/api/interpreter?data=[out:xml][maxsize:500000000][timeout:300];{}out body;'

def GetUrl(url, fileName):
    r = requests.get(url, headers={'Referer': 'https://www.saia-pcd.com'}, stream=True)
    if r.status_code == 200:
        with open(fileName, 'wb') as out:
            for chunk in r.iter_content(1024):
                out.write(chunk)
        print('Created {}: {}'.format(fileName, url))
    else:
        print('Failed: {} {}: {}'.format(r.status_code, r.reason, url))

def GetArea(query, fileName, raw=False):
    if raw:
        url = urlFmt.format(query)
    else:
        url = urlFmt.format(query + r'->.X;(node(area.X);<;);')
    GetUrl(url, fileName)

def getBox(south, west, north, east, fileName):
    q = urlFmt.format('(node({},{},{},{});<;);'.format(south,west,north,east))
    GetUrl(q, fileName)

    
def someAreaTest():
    GetArea(r'area[name="Fribourg/Freiburg"][boundary=administrative][admin_level=4]', 'Fribourg.osm')
    GetArea(r'relation(1718788);node(around:300);<;->.X;', '3Rivieres.osm', True)
    GetArea(r'(node(329205815);node(around:5000);<;);', 'Alba.osm', True)

def areaUnionTest():
    GetArea(r'('
         r'area[name="Fribourg/Freiburg"][boundary=administrative][admin_level=4];'
         r'area[name~"^District .*Aigle$"][type=boundary][boundary=administrative][admin_level=6];'
         r')', 'Fribourg-plus.osm')


def polyIntersectionTest():
    poly = [46.70126,7.02301,46.70126,7.27776,46.87427,7.27776,46.87427,7.02301,46.70126,7.02301]
    poly1 = [46.83953,7.13768,46.81745,7.06284,46.78172,7.09373,46.75539,7.12051,46.75492,7.16789,46.77514,7.20634,46.82544,7.20360,46.83953,7.13768]

    q = '(' \
            'node(poly:"{}");' \
            '- node(poly:"{}");' \
        ');' \
        '(' \
            '._;' \
            '<;' \
        ');'.format(' '.join([str(x) for x in poly]), ' '.join([str(x) for x in poly1]))
    GetUrl(urlFmt.format(q), 'AA.osm')

def polySimpleTest():
    poly = '''
        node(poly:"42.70363 10.09403 42.70363 10.45383 42.87622 10.45383 42.87622 10.09403 42.70363 10.09403");
        ( ._; <;);
    '''
    GetUrl(urlFmt.format(poly), 'Elba.osm')

def boundingSimpleTest():
    getBox(42.73,10.25,42.82,10.34, 'Elba1.osm')

def getAreaWithBoundingBox():
    b = '&bbox=114.41162,-8.87964,116.12823,-8.02388'

def areaIntersectionTest():
    q = '''
        (
            area[name="Fribourg/Freiburg"][boundary=administrative][admin_level=4];
            area[name~"^District .*Aigle$"][boundary=administrative][admin_level=6];
        )->.include;
        (
            area[name="Marly"][boundary=administrative][admin_level=8];
            area[name="Villars-sur-Glâne"][boundary=administrative][admin_level=8];
        )->.exclude;
        (
            ( node(area.include); - node(area.exclude); ); (._;<;);
            ( way(area.include); - way(area.exclude); ); (._;<;);
            ( relation(area.include); - relation(area.exclude); ); (._;<<;);
        );
    '''
    #f = urlFmt.format(''.join(q.split()))
    f = urlFmt.format(q)
    GetUrl(f, 'AA1.osm')


def compareTest():
    f = urlFmt.format('(area[name="Fribourg/Freiburg"][boundary=administrative][admin_level=4];)->.X;(node(area.X);<;);')
    GetUrl(f, 'AA1.osm')
    f = urlFmt.format('(area[name="Fribourg/Freiburg"][boundary=administrative][admin_level=4];)->.X;(node(area.X);<;way(area.X);<;relation(area.X);<<;);')
    GetUrl(f, 'AA2.osm')

if __name__ == '__main__':
    boundingSimpleTest()

