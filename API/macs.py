from config import db
from models import (
    MacAddress,
    MacAddressSchema,
    GoesAlong,
    GoesAlongSchema
)
from flask import abort, make_response

def read_pictures(address):
    goes_along = GoesAlong.query\
            .filter(GoesAlong.fk_mac==address).all()

    if goes_along is not None:
        goes_along_scheme = GoesAlongSchema(many=True)
        return goes_along_scheme.dump(goes_along)
    else:
        abort(404, "No pictures found for the address {address}".format(address=address))

def read_all():
    macs = MacAddress.query.order_by(MacAddress.address).all()

    # Serialize the data for the response
    macs_scheme = MacAddressSchema(many=True)
    return macs_scheme.dump(macs)

def create(mac):

    schema = MacAddressSchema()
    new_mac = schema.load(mac, session=db.session)

    macDB = MacAddress.query \
        .filter(MacAddress.address==new_mac.address) \
        .one_or_none()

    if macDB is not None:
        abort(409, 'MAC {address} already exist'.format(address=new_mac.address))

    # Add the person to the database
    db.session.add(new_mac)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_mac), 201


def read_one(address):
    mac = MacAddress.query \
        .filter(MacAddress.address== address) \
        .one_or_none()

    if mac is not None:
        probe_schema = MacAddressSchema()
        return probe_schema.dump(mac)
    else:
        abort(404, 'MAC {address} not found'.format(address=address))

def delete(address):
    mac = MacAddress.query.filter(MacAddress.address == address).one_or_none()

    if mac is not None:
        db.session.delete(mac)
        db.session.commit()
        return make_response(
            "MAC Address {address} deleted".format(address=address), 200
        )

    else:
        abort(
            404,
            "MAC Address {address} not found".format(probe_id=id),
        )
