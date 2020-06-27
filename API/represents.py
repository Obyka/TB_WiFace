from config import db
from models import (
    Identities,
    IdentitiesSchema,
    Pictures,
    PicturesSchema,
    Represents,
    RepresentsSchema
)
from flask import abort, make_response
from flask_jwt_extended import jwt_required

@jwt_required
def create(represent):
    schema = RepresentsSchema()
    new_rep = schema.load(represent, session=db.session)

    # Add the person to the database
    db.session.add(new_rep)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_rep), 201

@jwt_required
def read_relationship(id_picture, id_identity):
    represent = Represents.query\
            .filter(Represents.fk_picture==id_picture, Represents.fk_identity==id_identity).one_or_none()

    if represent is not None:
        represent_scheme = RepresentsSchema()
        return represent_scheme.dump(represent)
    else:
        abort(404, "Association {id_picture} - {id_identity} not found".format(id_picture=id_picture, id_identity=id_identity))

@jwt_required
def delete(id_picture, id_identity):
    represent = Represents.query.filter(Represents.fk_identity == id_identity, Represents.fk_picture == id_picture).one_or_none()

    if represent is not None:
        db.session.delete(represent)
        db.session.commit()
        return '', 204
    else:
        abort(
            404,
            "Relationship {id_identity} - {id_picture} not found".format(id_identity=id_identity, id_picture=id_picture),
        )
