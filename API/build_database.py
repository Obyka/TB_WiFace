import os
from datetime import datetime, timedelta
from xml.dom import minidom

from botocore.exceptions import ClientError

from config import app, db, boto_client
from models import (Identities, MacAddress, Pictures, Places,
                    Probes, Represents, User, Vendors)


def create_collection(collection_id, client):
    # Create a collection
    print('Creating collection:' + collection_id)
    response = client.create_collection(CollectionId=collection_id)
    print('Collection ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Done...')


def delete_collection(collection_id, client):
    print('Attempting to delete collection ' + collection_id)
    status_code = 0
    try:
        response = client.delete_collection(CollectionId=collection_id)
        status_code = response['StatusCode']

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print('The collection ' + collection_id + ' was not found ')
        else:
            print('Error other than Not Found occurred: ' +
                  e.response['Error']['Message'])
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        print('Status code: ' + str(status_code))


def main():
    collection_id = app.config['COLLECTION_NAME']
    delete_collection(collection_id, client)
    create_collection(collection_id, client)

    # Data to initialize database with
    xmldoc = minidom.parse('vendors.xml')
    VendorsList = xmldoc.getElementsByTagName('VendorMapping')

    MACS = [
        {"address": "11:11:11:11:11:11", "isRandom": False, "fk_vendor": "DC:F0:90", "PP2I" : False},
        {"address": "22:22:22:22:22:22", "isRandom": True, "fk_vendor": "E0:02:A5", "PP2I" : True},
        {"address": "33:33:33:33:33:33", "isRandom": False, "fk_vendor": "FC:F8:AE", "PP2I" : True},
        {"address": "44:44:44:44:44:44", "isRandom": False, "fk_vendor": "FC:F8:AE", "PP2I" : True}
    ]

    PLACES = [
        {"id": 1, "name": "BatCave", "longitude": 6.869948, "latitude": 46.457080},
        {"id": 2, "name": "Toussaint", "longitude": 22, "latitude": 9},
        {"id": 3, "name": "Aperture Science", "longitude": 42, "latitude": 42}
    ]

    USERS = [
        {"email": "Obyka", "password": User.hash("pass"), "admin": True, "fk_place":1},
        {"email": "Raspberry", "password": User.hash("pass"), "admin": False, "fk_place":2}
    ]

    IDENTITIES = [
        {"id": 1, "firstname": "Bruce", "lastname": "Wayne", "mail": "batman", "uuid": "f8d9c454-443e-45d0-937f-17b676dd6fde", "PP2I" : False},
        {"id": 2, "firstname": "Clark", "lastname": "Kent", "mail": "superman", "uuid": "3cf2fca0-f743-415b-ac3d-728121d64bae", "PP2I" : True},
        {"id": 3, "firstname": "Tony", "lastname": "Stark", "mail": "ironman", "uuid": "629fa6e3-4b6b-49d4-abef-29829c1f860e", "PP2I" : False},
        {"id": 4, "firstname": "Diana", "lastname": "Prince", "mail": "wonderwoman", "uuid": "729fa6e3-4b6b-49d4-abef-29829c1f860e", "PP2I" : False}
    ]

    probe_time = timedelta(minutes=(2))
    batman_time = datetime.utcnow()
    superman_time = batman_time + timedelta(minutes=(20))
    ironman_time = batman_time + timedelta(minutes=(25))
    wonderwoman = ironman_time

    PICTURES = [
        {"id": 1, "picPath": "batman.jpg", "timestamp": batman_time, "fk_place": 1},
        {"id": 2, "picPath": "superman.jpg", "timestamp": superman_time, "fk_place": 1},
        {"id": 3, "picPath": "ironman.jpg", "timestamp": ironman_time, "fk_place": 1},
        {"id": 4, "picPath": "wonderwoman.jpg", "timestamp": wonderwoman, "fk_place": 2},
        {"id": 5, "picPath": "batman_no_mac.jpg", "timestamp": batman_time + timedelta(hours=1), "fk_place": 1},
    ]

    PROBES = [
        {"ssid": "probe_ssid_1", "timestamp": batman_time + probe_time, "fk_mac": "11:11:11:11:11:11", "fk_place": 1},
        {"ssid": "probe_ssid_2", "timestamp": batman_time - probe_time, "fk_mac": "11:11:11:11:11:11", "fk_place": 2},
        {"ssid": "probe_ssid_3", "timestamp": superman_time + probe_time, "fk_mac": "22:22:22:22:22:22", "fk_place": 1},
        {"ssid": "probe_ssid_3", "timestamp": superman_time - probe_time, "fk_mac": "22:22:22:22:22:22", "fk_place": 1},
        {"ssid": "probe_ssid_1", "timestamp": ironman_time + probe_time, "fk_mac": "33:33:33:33:33:33", "fk_place": 1},
        {"ssid": "probe_ssid_2", "timestamp": ironman_time - probe_time, "fk_mac": "33:33:33:33:33:33", "fk_place": 1},
        {"ssid": "probe_ssid_3", "timestamp": wonderwoman + probe_time, "fk_mac": "44:44:44:44:44:44", "fk_place": 1},
        {"ssid": "probe_ssid_3", "timestamp": wonderwoman - probe_time, "fk_mac": "44:44:44:44:44:44", "fk_place": 1}
    ]
    REPRENSENTS = [
        {"probability": 100, "fk_identity": 1, "fk_picture": 1},
        {"probability": 100, "fk_identity": 1, "fk_picture": 5},
        {"probability": 100, "fk_identity": 2, "fk_picture": 2},
        {"probability": 100, "fk_identity": 3, "fk_picture": 3},
        {"probability": 100, "fk_identity": 4, "fk_picture": 4}
    ]

    # Delete database file if it exists currently
    if os.path.exists('probes.db'):
        os.remove('probes.db')

    # Create the database
    db.create_all()

    # Iterate over the PEOPLE structure and populate the database

    for vendor in VendorsList:
        v = Vendors(name=vendor.attributes['vendor_name'].value,
                    oui=vendor.attributes['mac_prefix'].value.upper())
        # print(vendor.attributes['mac_prefix'].value.upper())
        db.session.add(v)
    db.session.flush()

    for mac in MACS:
        m = MacAddress(
            address=mac['address'], isRandom=mac['isRandom'], fk_vendor=mac['fk_vendor'], PP2I=mac['PP2I'])
        db.session.add(m)
    db.session.flush()

    for place in PLACES:
        p = Places(id=place['id'], name=place['name'], latitude=place['latitude'], longitude=place['longitude'])
        db.session.add(p)
    db.session.flush()

    for probe in PROBES:
        p = Probes(ssid=probe['ssid'], timestamp=probe['timestamp'],
                   fk_mac=probe['fk_mac'], fk_place=probe['fk_place'])
        db.session.add(p)
    db.session.flush()

    for user in USERS:
        u = User(email=user['email'], password=user['password'], admin=user['admin'], fk_place=user['fk_place'])
        db.session.add(u)
    db.session.flush()

    for identity in IDENTITIES:
        i = Identities(id=identity['id'], firstname=identity['firstname'],
                       lastname=identity['lastname'], mail=identity['mail'], uuid=identity['uuid'], PP2I=identity['PP2I'])
        db.session.add(i)
    db.session.flush()

    for picture in PICTURES:
        p = Pictures(id=picture['id'], picPath=picture['picPath'],
                     timestamp=picture['timestamp'], fk_place=picture['fk_place'])
        db.session.add(p)
    db.session.flush()

    for represents in REPRENSENTS:
        r = Represents(probability=represents['probability'],
                       fk_identity=represents['fk_identity'], fk_picture=represents['fk_picture'])
        db.session.add(r)
    db.session.flush()

    db.session.commit()


if __name__ == "__main__":
    client = boto_client
    main()
