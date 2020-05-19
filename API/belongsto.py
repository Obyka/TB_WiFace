from config import db
from models import (
    Pictures,
    PicturesSchema,
    MacAddress,
    MacAddressSchema,
    BelongsTo,
    BelongsToSchema
)
from flask import abort, make_response
from flask_jwt_extended import jwt_required

@jwt_required
def read_identites(address, id):
    belongs_to = BelongsTo.query\
            .filter(BelongsTo.fk_mac==address, BelongsTo.fk_identity==id).one_or_none()

    if belongs_to is not None:
        belongs_to_scheme = BelongsToSchema()
        return belongs_to_scheme.dump(belongs_to)
    else:
        abort(404, "Association {address} - {id} not found".format(address=address, id=id))

@jwt_required
def create(belongsto):
    schema = BelongsToSchema()
    new_belongsto = schema.load(belongsto, session=db.session)

    # Add the person to the database
    db.session.add(new_belongsto)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_belongsto), 201

@jwt_required
def delete(address, id):
    belongsTo = BelongsTo.query.filter(BelongsTo.fk_mac == address, BelongsTo.fk_identity == id).one_or_none()

    if belongsTo is not None:
        db.session.delete(belongsTo)
        db.session.commit()
        return make_response(
            "Relationship {address} - {id} deleted".format(id=id, address=address), 200
        )

    else:
        abort(
            404,
            "Relationship {address} - {id} not found".format(id=id, address=address),
        )
