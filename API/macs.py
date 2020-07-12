from flask import abort, make_response
from flask_jwt_extended import jwt_required

import places
import probes
import vendors
from config import db
from models import BelongsTo, BelongsToSchema, MacAddress, MacAddressSchema


def count_random():
    return MacAddress.query.filter(MacAddress.isRandom == True).count()


def count():
    return MacAddress.query.count()


def get_mac_infos(mac):
    vendor = vendors.read_by_oui(mac['fk_vendor'])
    mac['vendor_name'] = vendor['name']
    mac['nb_probes'] = len(mac['probes'])
    mac['places'] = []

    places_set = set()
    for probe in mac['probes']:
        probe_data = probes.read_one(probe)
        places_set.add(probe_data['fk_place'])

    for place in places_set:
        mac['places'].append(places.read_one(place))
    return mac


@jwt_required
def read_identities(address):
    belongs_to = BelongsTo.query\
        .filter(BelongsTo.fk_mac == address).all()

    if belongs_to is not None:
        belongs_to_scheme = BelongsToSchema(many=True)
        return belongs_to_scheme.dump(belongs_to)
    else:
        abort(404, "No identities found for the address {address}".format(address=address))


@jwt_required
def read_all():
    macs = MacAddress.query.order_by(MacAddress.address).all()

    # Serialize the data for the response
    macs_scheme = MacAddressSchema(many=True)
    return macs_scheme.dump(macs)


@jwt_required
def create(mac):
    schema = MacAddressSchema()
    new_mac = schema.load(mac, session=db.session)

    macDB = MacAddress.query \
        .filter(MacAddress.address == new_mac.address) \
        .one_or_none()

    if macDB is not None:
        abort(409, 'MAC {address} already exist'.format(address=new_mac.address))

    # Add the person to the database
    db.session.add(new_mac)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_mac), 201

@jwt_required
def edit_pp2i(address, pp2i):
    macDB = MacAddress.query \
        .filter(MacAddress.address == address) \
        .one_or_none()

    if macDB is None:
        abort(404, 'MAC {address} does not exist'.format(address=address))

    macDB.PP2I = pp2i 
    db.session.commit()

    # Serialize and return the newly created person in the response
    return 201

@jwt_required
def read_one(address):
    mac = MacAddress.query \
        .filter(MacAddress.address == address) \
        .one_or_none()

    if mac is not None:
        probe_schema = MacAddressSchema()
        return probe_schema.dump(mac)
    else:
        abort(404, 'MAC {address} not found'.format(address=address))


@jwt_required
def delete(address):
    mac = MacAddress.query.filter(MacAddress.address == address).one_or_none()

    if mac is not None:
        db.session.delete(mac)
        db.session.commit()
        return '', 204

    else:
        abort(404, "MAC Address {address} not found".format(probe_id=id))
