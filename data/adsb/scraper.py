import sys
import requests
import time
import pymysql as my
import json
import pprint

## This program scrapes the necessary ads-b data from Flightradar24

# Url to flightradar24 feed
base_url = "http://data-live.flightradar24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=0" \
           "&adsb=1&gnd=1&air=1&vehicles=0&estimated=0&" \
           "maxage=0&gliders=0&stats=1"

# area to consider [lat, lat, lon, lon]
zones = [
    [60, 48, -12, 21],
    [60, 48, 21, 30],
    [48, 35, -12, 21],
    [48, 35, 21, 30]
]
#
# scrapertime =   #time to scrape in seconds
# Connect with the MySQL server
db = my.connect(host="localhost", user="root", passwd="atmresearch2017", db="flightdata")
c = db.cursor()


def read_ac_data(key, data):
    try:
        if not data[0]:  # ICAO not empty
            return None

        ac = {}
        ac['fid'] = key
        ac['icao'] = data[0]
        ac['lat'] = data[1]
        ac['lon'] = data[2]
        ac['hdg'] = data[3]
        ac['alt'] = data[4]
        ac['spd'] = data[5]  # horizontal speed
        ac['mdl'] = data[8]
        ac['regid'] = data[9]  # Registration ID
        ac['ts'] = data[10]
        ac['or'] = data[11]  # Origin
        ac['des'] = data[12]  # Destination
        ac['gnd'] = data[14]  # status on ground
        ac['roc'] = data[15]  # vertical rate
        ac['fn'] = data[16]  # flight number
        return ac

    except:
        return None


s = requests.Session()
s.headers.update({'user-agent': 'Mozilla/5.0'})

start = time.time()

while True:
    tic = time.time()
    data = []

    for zone in zones:
        bounds = ','.join(str(z) for z in zone)
        url = base_url + "&bounds=" + bounds
        print(url)

        try:
            r = s.get(url)
            if r.status_code != 200:
                continue

            try:
                res = r.json()

            except Exception as e:
                print(e)
                continue

            if len(res) < 3:
                continue

            for key, val in res.items():

                ac = read_ac_data(key, val)

                if not ac:
                    continue

                data.append(ac)
        except Exception as e:
            print(e)

    toc = time.time() - tic
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    print("%s: %d seconds, %d rows fetch" % (now, toc, len(data)))

    for i in range(0, len(data), 1):
        aircraft = data[i]

        org = str(aircraft['or'])
        des = str(aircraft['des'])
        icao = str(aircraft['icao'])
        regid = str(aircraft['regid'])
        mdl = str(aircraft['mdl'])
        fn = str(aircraft['fn'])
        lon = aircraft['lon']
        lat = aircraft['lat']
        hdg = aircraft['hdg']
        alt = aircraft['alt']
        spd = aircraft['spd']
        ts = aircraft['ts']
        roc = aircraft['roc']

        try:
            c.execute("""INSERT INTO eurotest1 (icao,org,des,regid,mdl,fn,lon,lat,hdg,alt,spd,ts,roc) 
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                  [icao, org, des, regid, mdl, fn, lon, lat, hdg, alt, spd, ts, roc])
            db.commit()
        except my.err.Dataerror as e:
            print(e)
    if time.time() - start > 28800:
        print('completed')
        db.close()
        break

    time.sleep(10)
