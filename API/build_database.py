import os
from config import db
from models import Probes
from datetime import datetime

# Data to initialize database with
PROBES = [
{"ssid": "probe_ssid_1", "timestamp": datetime.utcnow(), "fk_mac" : 1, "fk_place" : 1},
{"ssid": "probe_ssid_2", "timestamp": datetime.utcnow(), "fk_mac" : 2, "fk_place" : 2},
{"ssid": "probe_ssid_3", "timestamp": datetime.utcnow(), "fk_mac" : 3, "fk_place" : 3}
]

# Delete database file if it exists currently
if os.path.exists('probes.db'):
    os.remove('probes.db')

# Create the database
db.create_all()

# Iterate over the PEOPLE structure and populate the database
for probe in PROBES:
    p = Probes(ssid=probe['ssid'], timestamp=probe['timestamp'], fk_mac=probe['fk_mac'], fk_place=probe['fk_mac'])
    db.session.add(p)

db.session.commit()