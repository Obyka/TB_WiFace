import json
import os

from flask import abort, make_response, request
from flask_jwt_extended import jwt_required
from flask_restful import reqparse
from sqlalchemy import literal

from config import db
from models import Pictures, PicturesSchema, Probes, ProbesSchema, Represents


def count():
    return Pictures.query.count()


def first(elem):
    return elem[0]


def feed():
    pictures = db.session.query(Pictures.timestamp.label('timestamp'), literal("Picture").label('Type')).limit(10).all()
    probes = db.session.query(Probes.timestamp.label('timestamp'), literal("Probe").label('Type')).limit(10).all()
    pictures.extend(probes)
    pictures.sort(key=first)
    return pictures


@jwt_required
def upload():
    #parser = reqparse.RequestParser()
    #parser.add_argument('upfile', type=FileStorage, location='files',help=parser_help1, required=True)
    #args = parser.parse_args()
    UPLOAD_DIRECTORY = './'
    with open(os.path.join(UPLOAD_DIRECTORY, "test.png"), "wb") as fp:
        fp.write(request.data)
    return 201


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
def read_best_pic(id_identity):
    picture = Pictures.query\
        .join(Represents, Pictures.id == Represents.fk_picture) \
        .filter(Represents.fk_identity == id_identity) \
        .order_by(Represents.probability) \
        .first()

    if picture is not None:
        picture_schema = PicturesSchema()
        return picture_schema.dump(picture)
    else:
        abort(404, 'Best picture for {id_identity} not found'.format(id_identity=id_identity))


@jwt_required
def delete(id):
    picture = Pictures.query.filter(Pictures.id == id).one_or_none()

    if picture is not None:
        db.session.delete(picture)
        db.session.commit()
        return '', 204
    else:
        abort(
            404,
            "Picture with the id {id} not found".format(id=id),
        )
