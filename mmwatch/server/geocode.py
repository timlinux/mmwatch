#!/usr/bin/env python
import urllib2
import json
from db import database, Change

QUERYAT_URL = 'http://tile.osmz.ru/queryat/'
BATCH_COUNT = 20


def geocode(lon, lat):
    """Returns a country by these coordinates."""
    try:
        url = '{0}qr?lon={1}&lat={2}'.format(QUERYAT_URL, lon, lat)
        resp = urllib2.urlopen(url)
        data = json.load(resp)
        if 'countries' in data and len(data['countries']) > 0:
            c = data['countries'][0]
            return c['en' if 'en' in c else 'name'].encode('utf-8')
        print('Could not geocode: {0}'.format(url))
    except urllib2.HTTPError:
        print('HTTPError: ' + url)
    except urllib2.URLError:
        print('URLError: ' + url)
    return None


def add_countries():
    database.connect()
    with database.atomic():
        q = Change.select().where((Change.country >> None) & (Change.action != 'a') & (~Change.changes.startswith('[[null, null]'))).limit(BATCH_COUNT)
        for ch in q:
            coord = ch.changed_coord()
            if coord is not None:
                country = geocode(coord[0], coord[1])
                if country is not None:
                    ch.country = country[:150]
                    ch.save()
            else:
                print('Empty coordinates: {0} {1} {2}'.format(ch.id, ch.action, ch.changes.encode('utf-8')))


if __name__ == '__main__':
    add_countries()
