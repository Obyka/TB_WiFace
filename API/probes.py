from flask import abort, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_claims

from config import db
from models import Probes, ProbesSchema


def count():
    return Probes.query.count()


@jwt_required
def read_all():
    """
    This function responds to a request for /api/probes
    with the complete lists of people
    :return:        json string of list of probes
    """
    # Create the list of probes from our data
    probes = Probes.query.order_by(Probes.ssid).all()

    # Serialize the data for the response
    probes_scheme = ProbesSchema(many=True)
    return probes_scheme.dump(probes)


@jwt_required
def create(probe):
    """
    This function creates a new probe

    based on the passed-in probe data

    :param probe:  probe to create
    :return:        201 on success
    """
    schema = ProbesSchema()
    new_probe = schema.load(probe, session=db.session)
    claims = get_jwt_claims()
    fk_place = claims['fk_place']
    new_probe.fk_place = fk_place


    db.session.add(new_probe)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_probe), 201


@jwt_required
def read_one(id):
    probe = Probes.query \
        .filter(Probes.id == id) \
        .one_or_none()

    if probe is not None:
        probe_schema = ProbesSchema()
        return probe_schema.dump(probe)
    else:
        abort(404, 'Probe not found for Id: {probe_id}'.format(probe_id=id))


@jwt_required
def delete(id):
    probe = Probes.query.filter(Probes.id == id).one_or_none()

    if probe is not None:
        db.session.delete(probe)
        db.session.commit()
        return '', 204

    else:
        abort(404, "Probe not found for Id: {probe_id}".format(probe_id=id))
