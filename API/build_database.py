import os
from config import db
from models import Probes, MacAddress, Places, Identities, Pictures, GoesAlong, Represents
from datetime import datetime

# Data to initialize database with
PROBES = [
{"ssid": "probe_ssid_1", "timestamp": datetime.utcnow(), "fk_mac" : "FF:FF:FF:FF:FF:FF", "fk_place" : 1},
{"ssid": "probe_ssid_2", "timestamp": datetime.utcnow(), "fk_mac" : "FF:FF:FF:FF:FF:EF", "fk_place" : 2},
{"ssid": "probe_ssid_3", "timestamp": datetime.utcnow(), "fk_mac" : "FF:FF:AB:FF:FF:FF", "fk_place" : 3}
]

MACS = [
    {"address" : "FF:FF:FF:FF:FF:FF", "isRandom" : False, "fk_vendor" : 1},
    {"address" : "FF:FF:FF:FF:FF:EF", "isRandom" : True, "fk_vendor" : 2},
    {"address" : "FF:FF:AB:FF:FF:FF", "isRandom" : False, "fk_vendor" : 3}
]

PLACES = [
    {"id":1, "name" : "BatCave", "longitude" : 12.2, "latitude" : 13.4},
    {"id":2, "name" : "Toussaint", "longitude" : 22, "latitude" : 9},
    {"id":3, "name" : "Aperture Science", "longitude" : 42, "latitude" : 42}
]

IDENTITIES = [
    {"id":1,"firstname" : "Bruce", "lastname" : "Wayne", "mail" : "bruce.wayne@iamnotbatman.com"},
    {"id":2,"firstname" : "Geralt", "lastname" : "De Riv", "mail" : "thewhitewolf@gmail.com"},
    {"id":3,"firstname" : "Florian", "lastname" : "Polier", "mail" : "florian.polier@heig-vd.ch"}
]

PICTURES = [
    {"id":1,"picPath" : "/tmp/test.png", "timestamp" : datetime.utcnow(), "fk_place" : 1},
    {"id":2,"picPath" : "/tmp/test2.png", "timestamp" : datetime.utcnow(), "fk_place" : 2},
    {"id":3,"picPath" : "/tmp/test3.png", "timestamp" : datetime.utcnow(), "fk_place" : 3},
]

REPRENSENTS = [
    {"probability" : 50, "fk_identity" : 1, "fk_picture" : 1},
    {"probability" : 60, "fk_identity" : 2, "fk_picture" : 2},
    {"probability" : 10, "fk_identity" : 3, "fk_picture" : 3}
] 


GOESALONG = [
    {"probability" : 50, "fk_mac" : "FF:FF:FF:FF:FF:FF", "fk_picture" : 1},
    {"probability" : 50, "fk_mac" : "FF:FF:FF:FF:FF:FF", "fk_picture" : 2},
    {"probability" : 60, "fk_mac" : "FF:FF:FF:FF:FF:EF", "fk_picture" : 2},
    {"probability" : 10, "fk_mac" : "FF:FF:AB:FF:FF:FF", "fk_picture" : 3}
] 


# Delete database file if it exists currently
if os.path.exists('probes.db'):
    os.remove('probes.db')

# Create the database
db.create_all()

# Iterate over the PEOPLE structure and populate the database


for mac in MACS:
    m = MacAddress(address=mac['address'], isRandom=mac['isRandom'], fk_vendor=mac['fk_vendor'])
    db.session.add(m)

for probe in PROBES:
    p = Probes(ssid=probe['ssid'], timestamp=probe['timestamp'], fk_mac=probe['fk_mac'], fk_place=probe['fk_place'])
    db.session.add(p)

for place in PLACES:
    p = Places(id=place['id'], name=place['name'], latitude=place['latitude'], longitude=place['longitude'])
    db.session.add(p)

for identity in IDENTITIES:
    i = Identities(id=identity['id'],firstname=identity['firstname'], lastname=identity['lastname'], mail=identity['mail'])
    db.session.add(i)

for picture in PICTURES:
    p = Pictures(id=picture['id'], picPath=picture['picPath'], timestamp=picture['timestamp'], fk_place=picture['fk_place'])
    db.session.add(p)

for goes in GOESALONG:
    g = GoesAlong(probability=goes['probability'], fk_mac=goes['fk_mac'], fk_picture=goes['fk_picture'])
    db.session.add(g) 

for represents in REPRENSENTS:
    r = Represents(probability=represents['probability'], fk_identity=represents['fk_identity'], fk_picture=represents['fk_picture'])
    db.session.add(r)

db.session.commit()