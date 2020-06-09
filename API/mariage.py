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

half_window_duration = datetime.timedelta(minutes=5)


def pair_init():
    all_identities = Identities.query.all()
    dict_belongs_to = {}
    BelongsTo.query.delete()
    db.session.commit()
    for one_identity in all_identities:
         for one_represent in one_identity.represents:
            one_picture = Pictures.query.filter(Pictures.id == one_represent.fk_picture).one_or_none()
            begining = one_picture.timestamp - half_window_duration
            end = one_picture.timestamp + half_window_duration
            place = one_picture.fk_place

            # We retrieve all the probes emitted during the window of each picture
            probes = Probes.query.filter(Probes.timestamp > begining).filter(Probes.timestamp < end).filter(Probes.fk_place == place).all()
            # We create the couple if it does not exist yet or increase its probability
            for one_probe in probes:
                if (one_probe.fk_mac, one_identity.id) in dict_belongs_to:
                    dict_belongs_to[(one_probe.fk_mac, one_identity.id)] += 1000
                else:
                    dict_belongs_to[(one_probe.fk_mac, one_identity.id)] = 1000

    all_identities = set([i[1] for i in dict_belongs_to.keys()])
    for one_identity in all_identities:
        count = len(set([m[0] for m in dict_belongs_to.keys() if m[1] == one_identity]))
        for k, v in dict_belongs_to.items():
            if k[1] == one_identity:
                dict_belongs_to[k] /= count
    return dict_belongs_to

def ID_but_no_MAC(dict_belongs_to):
    for key_belongs_to, val_belongs_to in dict_belongs_to.items():
        one_identity = key_belongs_to[1]
        one_mac = key_belongs_to[0]
        all_pictures = Pictures.query.join(Represents).filter(Represents.fk_identity == one_identity)
        for one_picture in all_pictures:
            begining = one_picture.timestamp - half_window_duration
            end = one_picture.timestamp + half_window_duration
            place = one_picture.fk_place
            all_probes = Probes.query.filter(Probes.timestamp > begining).filter(Probes.timestamp < end).filter(Probes.fk_place == place).all()
            macs = list(set([p.fk_mac for p in all_probes]))
            if one_mac not in macs:
                dict_belongs_to[(one_mac, one_identity)] -= 500

    return dict_belongs_to

def MAC_but_no_ID(dict_belongs_to):
    for key_belongs_to, val_belongs_to in dict_belongs_to.items():
        one_identity = key_belongs_to[1]
        one_mac = key_belongs_to[0]
        all_probes = Probes.query.filter(Probes.fk_mac == one_mac)
        for one_probe in all_probes:
            begining = one_probe.timestamp - half_window_duration
            end = one_probe.timestamp + half_window_duration
            place = one_probe.fk_place
            all_represent = Represents.query.join(Pictures).filter(Represents.fk_picture == Pictures.id).filter(Pictures.timestamp > begining).filter(Pictures.timestamp < end).filter(Pictures.fk_place == place).all()
            all_identities = list(set([r.fk_identity for r in all_represent]))
            if one_identity not in all_identities:
                dict_belongs_to[(one_mac, one_identity)] -= 100
    return dict_belongs_to

def my_tanh(dict_belongs_to):
    new_dict_belongs_to = {}
    all_identities = set([i[1] for i in dict_belongs_to.keys()])
    for one_identity in all_identities:
        dict_mac = {key[0]:item for key, item in dict_belongs_to.items() if key[1] == one_identity}
        minP = min(dict_mac.values())
        maxP = max(dict_mac.values())
        print(dict_mac)
        print("AAAAH")
        for k in dict_mac.keys():
            # https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
            dict_mac[k] = 1. if maxP-minP == 0 else (dict_mac[k] - minP) / float(maxP - minP)
            new_dict_belongs_to[(k,one_identity)] = dict_mac[k]
    print(new_dict_belongs_to)

    return new_dict_belongs_to



def add_to_database(dict_belongs_to):
    BelongsTo_db = [BelongsTo(probability=item, fk_mac=key[0], fk_identity=key[1]) for key,item in dict_belongs_to.items()]
    db.session.add_all(BelongsTo_db)
    db.session.commit()
def mariage():
    final_values = my_tanh(MAC_but_no_ID(ID_but_no_MAC(pair_init())))
    add_to_database(final_values)
    #ID_but_no_MAC()
    #MAC_but_no_ID()
    #my_tanh()
    return str(final_values)