from config import db
from models import (
    Pictures,
    PicturesSchema,
    MacAddress,
    MacAddressSchema,
    GoesAlong,
    GoesAlongSchema
)
from flask import abort, make_response

def read_pictures(address, id):
    goes_along = GoesAlong.query\
            .filter(GoesAlong.fk_mac==address, GoesAlong.fk_picture==id).one_or_none()

    if goes_along is not None:
        goes_along_scheme = GoesAlongSchema()
        return goes_along_scheme.dump(goes_along)
    else:
        abort(404, "Association {address} - {id} not found".format(address=address, id=id))

def create(goesalong):
    schema = GoesAlongSchema()
    new_goesalong = schema.load(goesalong, session=db.session)

    # Add the person to the database
    db.session.add(new_goesalong)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_goesalong), 201

def delete(address, id):
    goesAlong = GoesAlong.query.filter(GoesAlong.fk_mac == address, GoesAlong.fk_picture == id).one_or_none()

    if goesAlong is not None:
        db.session.delete(goesAlong)
        db.session.commit()
        return make_response(
            "Relationship {address} - {id} deleted".format(id=id, address=address), 200
        )

    else:
        abort(
            404,
            "Relationship {address} - {id} not found".format(id=id, address=address),
        )
