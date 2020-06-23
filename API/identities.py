from config import db
from models import (
    Identities,
    IdentitiesSchema,
    Represents,
    RepresentsSchema
)
from flask import abort, make_response
from flask_jwt_extended import jwt_required

def count():
    return Identities.query.count()

@jwt_required
def read_pictures(id_identity):
    represent = Represents.query\
            .filter(Represents.fk_identity==id_identity).all()

    if represent is not None:
        represent_schema = RepresentsSchema(many=True)
        return represent_schema.dump(represent)
    else:
        abort(404, "No pictures found for the identity {id_identity}".format(id_identity=id_identity))

@jwt_required
def read_all():
    identities = Identities.query.order_by(Identities.lastname).all()

    # Serialize the data for the response
    Identities_scheme = IdentitiesSchema(many=True)
    return Identities_scheme.dump(identities)

@jwt_required
def create(identitiy):
    schema = IdentitiesSchema()
    new_identity = schema.load(identitiy, session=db.session)

    # Add the person to the database
    db.session.add(new_identity)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_identity), 201

@jwt_required
def read_one_by_uuid(uuid):
    identity = Identities.query \
        .filter(Identities.uuid == uuid) \
        .one_or_none()

    if identity is not None:
        identity_schema = IdentitiesSchema()
        return identity_schema.dump(identity)
    else:
        abort(404, 'identity with the id {uuid} not found'.format(uuid=uuid))

@jwt_required
def read_one(id):
    identity = Identities.query \
        .filter(Identities.id == id) \
        .one_or_none()

    if identity is not None:
        identity_schema = IdentitiesSchema()
        return identity_schema.dump(identity)
    else:
        abort(404, 'identity with the id {id} not found'.format(id=id))

@jwt_required
def delete(id):
    identity = Identities.query.filter(Identities.id == id).one_or_none()

    if identity is not None:
        db.session.delete(identity)
        db.session.commit()
        return make_response(
            "identity with the id {id} deleted".format(id=id), 200
        )

    else:
        abort(
            404,
            "identity with the id {id} not found".format(id=id),
        )
