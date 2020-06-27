from config import db
from models import (
    Places,
    PlacesSchema,
)
from flask import abort, make_response
from flask_jwt_extended import jwt_required

@jwt_required
def read_all():
    places = Places.query.order_by(Places.name).all()

    # Serialize the data for the response
    places_scheme = PlacesSchema(many=True)
    return places_scheme.dump(places)

@jwt_required
def create(place):
    schema = PlacesSchema()
    new_place = schema.load(place, session=db.session)

    # Add the person to the database
    db.session.add(new_place)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_place), 201

@jwt_required
def read_one(id):
    place = Places.query \
        .filter(Places.id == id) \
        .one_or_none()

    if place is not None:
        place_schema = PlacesSchema()
        return place_schema.dump(place)
    else:
        abort(404, 'Place with the id {id} not found'.format(id=id))

@jwt_required
def delete(id):
    place = Places.query.filter(Places.id == id).one_or_none()

    if place is not None:
        db.session.delete(place)
        db.session.commit()
        return '', 204

    else:
        abort(
            404,
            "Place with the id {id} not found".format(id=id),
        )
