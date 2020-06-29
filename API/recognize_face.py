import argparse
import os
import time
import uuid
from datetime import datetime, timedelta

import boto3

from config import app, db
from identities import read_one_by_uuid
from models import BelongsTo, Identities, Pictures, Places, Represents


def recognizeFace(client, image_name, collection):
    """[Check in an Amazon Rekognition collection if a given image contains one of its faces]

    Arguments:
        client {[object]} -- [boto3 client]
        image {[file]} -- [image to check]
        collection {[string]} -- [collection name]

    Returns:
        [bool] -- [Is the face in the collection ?]
        [type] -- [Amazon rekognition's response]
    """
    face_matched = False
    with open(image_name, 'rb') as file:
        response = client.search_faces_by_image(CollectionId=collection, Image={
                                                'Bytes': file.read()}, MaxFaces=1, FaceMatchThreshold=85)
        if (not response['FaceMatches']):
            face_matched = False
        else:
            face_matched = True
        return face_matched, response


def add_face_collection(collection, image_name, face_identity, client):
    """Index the face contained in an image and add it in a collection

    Arguments:
        collection {[string]} -- [Collection name where to add the face]
        image {[file]} -- [image to extract the face from]
        name {[type]} -- [identity UUID linked to the face]
    """
    with open(image_name, mode='rb') as file:
        response = client.index_faces(Image={'Bytes': file.read()}, CollectionId=collection,
                                      ExternalImageId=face_identity.uuid, DetectionAttributes=['ALL'])
    return response


def handle_picture(picture_file, picture_name):
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_name)
    # get args
    collection = app.config['COLLECTION_NAME']

    # initialize reckognition sdk
    client = boto3.client(
        'rekognition', aws_access_key_id=app.config['aws_access_key_id'], aws_secret_access_key=app.config['aws_secret_access_key'])
    try:
        face_matched, response = recognizeFace(client, picture_path, collection)
    except client.exceptions.InvalidParameterException as e:
        raise ValueError
    print('Face detected!')
    if (face_matched):
        print(response['FaceMatches'][0]['Face'])
        confidence = round(response['FaceMatches'][0]['Face']['Confidence'], 2)
        faceUUID = response['FaceMatches'][0]['Face']['ExternalImageId']
        similarity = round(response['FaceMatches'][0]['Similarity'], 1)
        get_identity = read_one_by_uuid(faceUUID)
        face_identity = Identities(id=get_identity['id'], uuid=get_identity['uuid'])
        print('Identity matched {} with {} similarity and {} confidence...'.format(faceUUID, similarity, confidence))
    else:
        print('Unknown Human Detected!')
        confidence = 100
        faceUUID = str(uuid.uuid4())
        face_identity = Identities(uuid=faceUUID)
        db.session.add(face_identity)
        db.session.flush()

    fullFaceResponse = add_face_collection(collection, picture_path, face_identity, client)
    faceDetails = fullFaceResponse['FaceRecords'][0]['FaceDetail']

    p = constructPictureObject(faceDetails, picture_name, 1)
    db.session.add(p)
    db.session.flush()
    r = Represents(probability=confidence, fk_identity=face_identity.id, fk_picture=p.id)
    db.session.add(r)
    db.session.flush()
    db.session.commit()


def constructPictureObject(faceDetails, picture_name, fk_place):
    booleanAttr = ['Eyeglasses', 'Sunglasses', 'Beard', 'Mustache']
    parsedDict = dict()
    for attribute in booleanAttr:
        attributeDetails = faceDetails[attribute]
        parsedDict[attribute.lower()] = attributeDetails['Confidence'] if attributeDetails['Value'] else - \
            attributeDetails['Confidence']

    parsedDict['ageMin'] = faceDetails['AgeRange']['Low']
    parsedDict['ageMax'] = faceDetails['AgeRange']['High']
    parsedDict['gender'] = faceDetails['Gender']['Confidence'] if faceDetails['Gender']['Value'] == 'Female' else - \
        faceDetails['Gender']['Confidence']

    for emotion in faceDetails['Emotions']:
        parsedDict[emotion['Type'].lower()] = emotion['Confidence']

    parsedDict['fk_place'] = fk_place
    parsedDict['picPath'] = picture_name
    parsedDict['timestamp'] = datetime.utcnow()

    return Pictures(**parsedDict)
