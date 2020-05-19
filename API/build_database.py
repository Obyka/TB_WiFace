import os
from config import db
from models import Probes, MacAddress, Places, Identities, Pictures, BelongsTo, Represents, Vendors, User
from datetime import datetime, timedelta
from xml.dom import minidom
# Data to initialize database with

xmldoc = minidom.parse('vendors.xml')
VendorsList = xmldoc.getElementsByTagName('VendorMapping')

USERS = [
    {"email":"Obyka", "password":User.hash("pass"), "admin":1}
]

PROBES = [
    {"ssid": "probe_ssid_1", "timestamp": datetime.utcnow(), "fk_mac" : "FF:FF:FF:FF:FF:FF", "fk_place" : 1},
    {"ssid": "probe_ssid_2", "timestamp": datetime.utcnow(), "fk_mac" : "FF:FF:FF:FF:FF:EF", "fk_place" : 1},
    {"ssid": "probe_ssid_3", "timestamp": datetime.utcnow(), "fk_mac" : "FF:FF:AB:FF:FF:FF", "fk_place" : 1},
    {"ssid": "probe_ssid_3", "timestamp": datetime.utcnow() + timedelta(minutes=10), "fk_mac" : "FF:FF:AB:FF:FF:AA", "fk_place" : 1}
]

MACS = [
    {"address" : "FF:FF:FF:FF:FF:FF", "isRandom" : False, "fk_vendor" : "DC:F0:90"},
    {"address" : "FF:FF:FF:FF:FF:EF", "isRandom" : True, "fk_vendor" : "E0:02:A5"},
    {"address" : "FF:FF:AB:FF:FF:FF", "isRandom" : False, "fk_vendor" : "FC:F8:AE"},
    {"address" : "FF:FF:AB:FF:FF:AA", "isRandom" : False, "fk_vendor" : "FC:F8:AE"}
]

PLACES = [
    {"id":1, "name" : "BatCave", "longitude" : 12.2, "latitude" : 13.4},
    {"id":2, "name" : "Toussaint", "longitude" : 22, "latitude" : 9},
    {"id":3, "name" : "Aperture Science", "longitude" : 42, "latitude" : 42}
]

IDENTITIES = [
    {"id":1,"firstname" : "Bruce", "lastname" : "Wayne", "mail" : "bruce.wayne@iamnotbatman.com", "uuid":"f8d9c454-443e-45d0-937f-17b676dd6fde"},
    {"id":2,"firstname" : "Geralt", "lastname" : "De Riv", "mail" : "thewhitewolf@gmail.com", "uuid":"3cf2fca0-f743-415b-ac3d-728121d64bae"},
    {"id":3,"firstname" : "Florian", "lastname" : "Polier", "mail" : "florian.polier@heig-vd.ch", "uuid":"629fa6e3-4b6b-49d4-abef-29829c1f860e"}
]

PICTURES = [
    {"id":1,"picPath" : "/tmp/test.png", "timestamp" : datetime.utcnow(), "fk_place" : 1},
    {"id":2,"picPath" : "/tmp/test2.png", "timestamp" : datetime.utcnow(), "fk_place" : 1},
    {"id":3,"picPath" : "/tmp/test3.png", "timestamp" : datetime.utcnow(), "fk_place" : 1},
]

REPRENSENTS = [
    {"probability" : 50, "fk_identity" : 1, "fk_picture" : 1},
    {"probability" : 60, "fk_identity" : 2, "fk_picture" : 2},
    {"probability" : 10, "fk_identity" : 3, "fk_picture" : 3},
    {"probability" : 100, "fk_identity" : 1, "fk_picture" : 3}
] 


BELONGSTO = [
    {"probability" : 50, "fk_mac" : "FF:FF:FF:FF:FF:FF", "fk_identity" : 1},
    {"probability" : 50, "fk_mac" : "FF:FF:FF:FF:FF:FF", "fk_identity" : 2},
    {"probability" : 60, "fk_mac" : "FF:FF:FF:FF:FF:EF", "fk_identity" : 2},
    {"probability" : 10, "fk_mac" : "FF:FF:AB:FF:FF:FF", "fk_identity" : 3}
] 


# Delete database file if it exists currently
if os.path.exists('probes.db'):
    os.remove('probes.db')

# Create the database
db.create_all()

# Iterate over the PEOPLE structure and populate the database

for vendor in VendorsList:
    v = Vendors(name=vendor.attributes['vendor_name'].value, oui=vendor.attributes['mac_prefix'].value.upper())
    #print(vendor.attributes['mac_prefix'].value.upper())
    db.session.add(v)

for user in USERS:
    u = User(email=user['email'], password=user['password'], admin=user['admin'])
    db.session.add(u)

""" for vendor in VENDORS:
    v = Vendors(oui=vendor['oui'], name=vendor['name'])
    db.session.add(v) """

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
    i = Identities(id=identity['id'],firstname=identity['firstname'], lastname=identity['lastname'], mail=identity['mail'], uuid=identity['uuid'])
    db.session.add(i)

for picture in PICTURES:
    p = Pictures(id=picture['id'], picPath=picture['picPath'], timestamp=picture['timestamp'], fk_place=picture['fk_place'])
    db.session.add(p)

for belongs in BELONGSTO:
    b = BelongsTo(probability=belongs['probability'], fk_mac=belongs['fk_mac'], fk_identity=belongs['fk_identity'])
    db.session.add(b) 

for represents in REPRENSENTS:
    r = Represents(probability=represents['probability'], fk_identity=represents['fk_identity'], fk_picture=represents['fk_picture'])
    db.session.add(r)

db.session.commit()