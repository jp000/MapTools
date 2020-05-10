# coding=utf-8


def coord(nbr, extra, minLat=-180.0, maxLat=180.0, minLon=-90.0, maxLon=90.0):
    deltaLat, deltaLon = (abs(minLat) + abs(maxLat)) / nbr, (abs(minLon) + abs(maxLon)) / nbr
    r = []
    lon = minLon
    while lon < maxLon:
        lat = minLat
        while lat < maxLat:
            #print(f'\'node({lon},{lat},{lon+deltaLon},{lat+deltaLat}){extra}\',')
            r.append(f'node({lon},{lat},{lon+deltaLon},{lat+deltaLat}){extra}')
            lat += deltaLat
        lon = lon+deltaLon
    return r

print (coord(2, '[place=village](if: number(t["population"]) >= 5000);out body;'))
print()
coord(5, '[place=village](if: number(t["population"]) >= 5000);out body;')

rint([x for x in xrange(-180.0, 180.0, 20)])