import os
from config import db
from models import Probes, MacAddress
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

# Delete database file if it exists currently
if os.path.exists('probes.db'):
    os.remove('probes.db')

# Create the database
db.create_all()

# Iterate over the PEOPLE structure and populate the database
for probe in PROBES:
    p = Probes(ssid=probe['ssid'], timestamp=probe['timestamp'], fk_mac=probe['fk_mac'], fk_place=probe['fk_place'])
    db.session.add(p)

for mac in MACS:
    m = MacAddress(address=mac['address'], isRandom=mac['isRandom'], fk_vendor=mac['fk_vendor'])
    db.session.add(m)

db.session.commit()