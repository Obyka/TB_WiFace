import json

from flask import Response, abort
from flask_jwt_extended import jwt_required

from config import db
from models import BelongsTo, BelongsToSchema, Identities


@jwt_required
def read_all():
    output = []
    for i, b  in db.session.query(Identities, BelongsTo).filter(Identities.id == BelongsTo.fk_identity).all():
        output.append((json.dumps({"values":[i.mail,b.fk_mac,b.probability]})))
    response = json.dumps({'belongs_to':output})
    return Response(response,  mimetype='application/json')

def read_by_identity(id):
    belongs_to = BelongsTo.query.filter(BelongsTo.fk_identity==id).all()
    if belongs_to is not None:
        belongs_to_scheme = BelongsToSchema(many=True)
        return belongs_to_scheme.dump(belongs_to)
    else:
        abort(404, "Identity {id} is not associated to any address".format(id=id))

@jwt_required
def read_identities(address, id):
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
        return '', 204
    else:
        abort(
            404,
            "Relationship {address} - {id} not found".format(id=id, address=address),
        )
