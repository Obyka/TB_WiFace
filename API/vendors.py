from config import db
from models import (
    Vendors,
    VendorsSchema,
)
from flask import abort, make_response
from flask_jwt_extended import jwt_required

#@jwt_required
def read_by_oui(oui):
    vendor = Vendors.query \
        .filter(Vendors.oui == oui) \
        .one_or_none()

    if vendor is not None:
        vendor_schema = VendorsSchema()
        return vendor_schema.dump(vendor)
    else:
        abort(404, 'Vendor with the OUI {oui} not found'.format(oui=oui))