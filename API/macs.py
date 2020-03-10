from config import db
from models import (
    MacAddress,
    MacAddressSchema,
)
from flask import abort, make_response

def read_all():
    macs = MacAddress.query.order_by(MacAddress.address).all()

    # Serialize the data for the response
    macs_scheme = MacAddressSchema(many=True)
    return macs_scheme.dump(macs)

def create(mac):
    schema = MacAddressSchema()
    new_mac = schema.load(mac, session=db.session)

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
