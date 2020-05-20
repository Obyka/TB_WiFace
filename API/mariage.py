import numpy as np
from config import db
import datetime
from flask import redirect, url_for
import json
from models import (
    Pictures,
    PicturesSchema,
    Probes,
    ProbesSchema,
    Identities,
    IdentitiesSchema,
    BelongsTo,
    BelongsToSchema,
    Represents
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

            for k1, v1 in dict_identities[one_identity.id].items():
                dict_identities[one_identity.id][k1] /= len(dict_identities[one_identity.id])

    output = ""
    for k1, v1 in dict_identities.items():
        for k2, v2 in v1.items():
            b = BelongsTo(probability=v2, fk_mac=k2, fk_identity=k1)
            output+=str(b)
            db.session.add(b)
    db.session.commit()
    return output

def ID_but_no_MAC():
    window_duration = datetime.timedelta(minutes=5)
    output=""
    all_belongs_to = BelongsTo.query.all()
    for one_belongs_to in all_belongs_to:
        one_identity = Identities.query.filter(Identities.id == one_belongs_to.fk_identity).one_or_none()
        one_mac = one_belongs_to.fk_mac
        all_pictures = Pictures.query.join(Represents).filter(Represents.fk_identity == one_identity.id)
        output += one_identity.mail + "\n"
        for one_picture in all_pictures:
            begining = one_picture.timestamp - window_duration
            end = one_picture.timestamp + window_duration
            place = one_picture.fk_place
            all_probes = Probes.query.filter(Probes.timestamp > begining).filter(Probes.timestamp < end).filter(Probes.fk_place == place).all()
            macs = list(set([p.fk_mac for p in all_probes]))
            if one_mac not in macs:
                output += "BEAUCOUP BAISSER"
                one_belongs_to.probability -= 500
                db.session.commit()
            output += one_picture.picPath + "\n"
            output += str(macs) + "\n"
    return output

def MAC_but_no_ID():
    window_duration = datetime.timedelta(minutes=5)
    output=""
    all_belongs_to = BelongsTo.query.all()
    for one_belongs_to in all_belongs_to:
        one_identity = Identities.query.filter(Identities.id == one_belongs_to.fk_identity).one_or_none()
        one_mac = one_belongs_to.fk_mac
        all_probes = Probes.query.filter(Probes.fk_mac == one_mac)
        for one_probe in all_probes:
            begining = one_probe.timestamp - window_duration
            end = one_probe.timestamp + window_duration
            place = one_probe.fk_place
            all_represent = Represents.query.join(Pictures).filter(Represents.fk_picture == Pictures.id).filter(Pictures.timestamp > begining).filter(Pictures.timestamp < end).filter(Pictures.fk_place == place).all()
            all_identities = list(set([r.fk_identity for r in all_represent]))
            if one_identity.id not in all_identities:
                one_belongs_to.probability -= 100
                db.session.commit()
                output += "UN PEU BAISSER "
            output+=one_probe.fk_mac + " " +str(all_identities) + "\n"
    return output

def my_tanh():
    identities = db.session.query(BelongsTo.fk_identity).distinct()
    for one_identity in identities:
            belongs_identity = db.session.query(BelongsTo).filter(BelongsTo.fk_identity == one_identity.fk_identity)
            belongs_identity_probability = [b.probability for b in belongs_identity]
            minP = np.min(belongs_identity_probability)
            maxP = np.max(belongs_identity_probability)
            for one_belong in belongs_identity:
                one_belong.probability = (one_belong.probability - minP) / (maxP - minP) * (maxP - minP) + minP
                db.session.commit()
def mariage():
    pair_init()
    ID_but_no_MAC()
    MAC_but_no_ID()
    #my_tanh()
    return redirect("/api/belongsto")