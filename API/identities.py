import functools

from flask import abort, make_response
from flask_jwt_extended import jwt_required

from config import db, boto_client, app
from models import (Identities, IdentitiesSchema, Pictures, PicturesSchema,
                    Represents, RepresentsSchema)
import aws_process

@jwt_required
def count():
    return Identities.query.count()

@jwt_required
def edit_identity(id_to_edit, identity):
    identity_schema = IdentitiesSchema()
    new_identity = identity_schema.load(identity)
    nb_row = db.session.query(Identities) \
        .filter_by(id = id_to_edit) \
        .update(dict(mail=new_identity.mail, firstname=new_identity.firstname, lastname=new_identity.lastname))

    if nb_row != 1:
        abort(500, 'The identity could not be modified.')
    db.session.commit()
    return 201

@jwt_required
def edit_pp2i(mail, pp2i):
    identityDB = Identities.query \
        .filter(Identities.mail == mail) \
        .one_or_none()

    if identityDB is None:
        abort(404, 'Identity {mail} does not exist'.format(mail=mail))

    identityDB.PP2I = pp2i 
    db.session.commit()
    return 201

@jwt_required
def read_age_range(id_identity):
    age_List = db.session.query(Pictures.ageMin, Pictures.ageMax)\
        .join(Represents, Pictures.id == Represents.fk_picture) \
        .filter(Represents.fk_identity == id_identity) \
        .all()

    age_List = [(r, s) for (r, s,) in age_List if r is not None and s is not None]
    if len(age_List) == 0:
        return None
    age_mean = (int(sum(i for i, j in age_List if i) / len(age_List)),
                int(sum(j for i, j in age_List if j) / len(age_List)))
    return age_mean

@jwt_required
def read_gender(id_identity):
    gender = Pictures.query\
        .with_entities(Pictures.gender)\
        .join(Represents, Pictures.id == Represents.fk_picture) \
        .filter(Represents.fk_identity == id_identity) \
        .all()

    gender_result = [r for (r, ) in gender if r is not None]
    return functools.reduce(lambda a, b: a+b, gender_result) if len(gender_result) > 0 else None


@jwt_required
def read_pictures(id_identity):
    represent = Represents.query\
        .filter(Represents.fk_identity == id_identity).all()

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
    face_ids = Pictures.query\
        .with_entities(Pictures.face_id)\
        .join(Represents, Pictures.id == Represents.fk_picture) \
        .filter(Represents.fk_identity == id) \
        .all()

    face_ids_result = [r for (r, ) in face_ids if r is not None]
    if len(face_ids_result) > 0:
        aws_process.delete_faces_from_collection(app.config['COLLECTION_NAME'],face_ids_result,boto_client)

    if identity is not None:
        db.session.delete(identity)
        db.session.commit()
        return '', 204

    else:
        abort(404,"identity with the id {id} not found".format(id=id))
