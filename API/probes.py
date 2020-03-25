from config import db
from models import (
    Probes,
    ProbesSchema,
)
from flask import abort, make_response
from flask import request

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

def create(probe):
    """
    This function creates a new probe

    based on the passed-in probe data

    :param probe:  probe to create
    :return:        201 on success
    """
    print(request.headers)
    schema = ProbesSchema()
    new_probe = schema.load(probe, session=db.session)

    # Add the person to the database
    db.session.add(new_probe)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_probe), 201


def read_one(id):
    probe = Probes.query \
        .filter(Probes.id == id) \
        .one_or_none()

    if probe is not None:
        probe_schema = ProbesSchema()
        return probe_schema.dump(probe)
    else:
        abort(404, 'Probe not found for Id: {probe_id}'.format(probe_id=id))

def delete(id):
    probe = Probes.query.filter(Probes.id == id).one_or_none()

    if probe is not None:
        db.session.delete(probe)
        db.session.commit()
        return make_response(
            "Probe {probe_id} deleted".format(probe_id=id), 200
        )

    else:
        abort(
            404,
            "Probe not found for Id: {probe_id}".format(probe_id=id),
        )
