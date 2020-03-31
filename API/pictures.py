from config import db
from models import (
    Pictures,
    PicturesSchema,
)
from flask import abort, make_response
from flask_jwt_extended import jwt_required

@jwt_required
def read_all():
    pictures = Pictures.query.order_by(Pictures.timestamp).all()

    # Serialize the data for the response
    pictures_scheme = PicturesSchema(many=True)
    return pictures_scheme.dump(pictures)

@jwt_required
def create(picture):
    schema = PicturesSchema()
    new_picture = schema.load(picture, session=db.session)

    # Add the person to the database
    db.session.add(new_picture)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_picture), 201

@jwt_required
def read_one(id):
    picture = Pictures.query \
        .filter(Pictures.id == id) \
        .one_or_none()

    if picture is not None:
        picture_schema = PicturesSchema()
        return picture_schema.dump(picture)
    else:
        abort(404, 'Picture with the id {id} not found'.format(id=id))

@jwt_required
def delete(id):
    picture = Pictures.query.filter(Pictures.id == id).one_or_none()

    if picture is not None:
        db.session.delete(picture)
        db.session.commit()
        return make_response(
            "Picture with the id {id} deleted".format(id=id), 200
        )

    else:
        abort(
            404,
            "Picture with the id {id} not found".format(id=id),
        )
