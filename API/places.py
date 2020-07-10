from flask import abort, make_response, Response, jsonify
from flask_jwt_extended import jwt_required

from config import db
from models import Places, PlacesSchema
import pictures
import identities
import represents


@jwt_required
def read_all():
    places = Places.query.order_by(Places.name).all()

    # Serialize the data for the response
    places_scheme = PlacesSchema(many=True)
    return places_scheme.dump(places)


def get_place_infos(place):
    emotions = ['happy', 'surprised', 'fear', 'confused', 'sad', 'calm', 'disgusted', 'angry']
    emotions_dictionary = dict.fromkeys(emotions, 0)
	# retire les trois expressions principales de la photo et les trie
	

    pictures_data = place['pictures']
    female = 0
    male = 0
    age_min_mean = 0
    age_max_mean = 0
    count_age_mean = 0
    total_emotion = 0
    identities_in_place = set()
    for picture in pictures_data:
        picture_details = pictures.read_one(picture)
        for emotion in emotions:
            add_emotion = picture_details.get(emotion) if picture_details.get(emotion) is not None else 0
            emotions_dictionary[emotion] += add_emotion
            total_emotion += add_emotion
        identities_in_place.update([r['fk_identity'] for r in represents.read_identities_from_picture(picture_details['id'])])

    for identity_in_place in identities_in_place:
        gender = identities.read_gender(identity_in_place)
        age_mean_identity = identities.read_age_range(identity_in_place)
        if age_mean_identity is not None:
            age_min_mean += age_mean_identity[0]
            age_max_mean += age_mean_identity[1]
            count_age_mean += 2
        if gender is not None:
            female, male = (female+1, male) if gender > 0 else (female, male+1)
    place['age_mean'] = int((age_min_mean + age_max_mean) / count_age_mean) if count_age_mean > 0 else None
    if male + female > 0:
        place['proportion'] = male / (female + male)
    else:
        place['proportion'] = 0
    place['emotions'] = emotions_dictionary
    place['total_emotion'] = total_emotion
    place['nb_identity'] = len(identities_in_place)
    place['nb_probes'] = len(place.get('probes'))
    return place

@jwt_required
def create(place):

    schema = PlacesSchema()
    new_place = schema.load(place, session=db.session)

    check_place = Places.query \
        .filter(Places.name == new_place.name) \
        .one_or_none()

    if check_place is not None:
        return '', Response(status=409)

    # Add the person to the database
    db.session.add(new_place)
    db.session.commit()

    # Serialize and return the newly created person in the response
    return schema.dump(new_place), 201


@jwt_required
def read_one(id):
    place = Places.query \
        .filter(Places.id == id) \
        .one_or_none()

    if place is not None:
        place_schema = PlacesSchema()
        return place_schema.dump(place)
    else:
        abort(404, 'Place with the id {id} not found'.format(id=id))


@jwt_required
def delete(id):
    place = Places.query.filter(Places.id == id).one_or_none()

    if place is not None:
        db.session.delete(place)
        db.session.commit()
        return '', 204

    else:
        abort(404, "Place with the id {id} not found".format(id=id))
