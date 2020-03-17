from config import db
from models import (
    Identities,
    IdentitiesSchema,
)
from flask import abort, make_response

def read_all():
    identities = Identities.query.order_by(Identities.lastname).all()

    # Serialize the data for the response
    Identities_scheme = IdentitiesSchema(many=True)
    return Identities_scheme.dump(identities)

def create(identitiy):
    schema = IdentitiesSchema()
    new_identity = schema.load(identitiy, session=db.session)

    # Add the person to the database
    db.session.add(new_identity)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_identity), 201


def read_one(id):
    identity = Identities.query \
        .filter(Identities.id == id) \
        .one_or_none()

    if identity is not None:
        identity_schema = IdentitiesSchema()
        return identity_schema.dump(identity)
    else:
        abort(404, 'identity with the id {id} not found'.format(id=id))

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
