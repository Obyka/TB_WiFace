from config import db
import datetime
import json
from models import (
    Pictures,
    PicturesSchema,
    Probes,
    ProbesSchema,
    Identities,
    IdentitiesSchema,
    BelongsTo,
    BelongsToSchema
)
from pictures import read_all as pictures_read_all
from pictures import read_one as pictures_read_one

def pair_init():
    # On veut supprimer tous les couples puisqu'on exécute le processus complet
    BelongsTo.query.delete()
    db.session.commit()

    window_duration = datetime.timedelta(minutes=5)
    all_identities = Identities.query.all()
    dict_identities = {}
    for one_identity in all_identities:
        dict_identities[one_identity.id] = {}
        for one_represent in one_identity.represents:
            one_picture = Pictures.query.filter(Pictures.id == one_represent.fk_picture).one_or_none()
            begining = one_picture.timestamp - window_duration
            end = one_picture.timestamp + window_duration
            place = one_picture.fk_place

            probes = Probes.query.filter(Probes.timestamp > begining).filter(Probes.timestamp < end).filter(Probes.fk_place == place).all()
            for one_probe in probes:
                if one_probe.fk_mac in dict_identities[one_identity.id]:
                    dict_identities[one_identity.id][one_probe.fk_mac] += 100
                else:
                    dict_identities[one_identity.id][one_probe.fk_mac] = 100

    print(dict_identities)
    for k1, v1 in dict_identities.items():
        for k2, v2 in v1.items():
            b = BelongsTo(probability=v2, fk_mac=k2, fk_identity=k1)
            db.session.add(b)
    db.session.commit()
    return "mariage executed"

def ID_but_no_MAC():
    pass

def MAC_but_no_ID():
    pass

def mariage():
    return pair_init()
