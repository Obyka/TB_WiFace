import argparse
import boto3
import time
from datetime import datetime, timedelta
from models import Places, Identities, Pictures, BelongsTo, Represents
from identities import read_one_by_uuid
import os
from config import db, app
import uuid


def recognizeFace(client,image_name,collection):
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
            response = client.search_faces_by_image(CollectionId=collection, Image={'Bytes': file.read()}, MaxFaces=1, FaceMatchThreshold=85)
            if (not response['FaceMatches']):
                face_matched = False
            else:
                face_matched = True
            return face_matched, response

def add_face_collection(collection, image_name, name, client, picture):
    """Index the face contained in an image and add it in a collection
    
    Arguments:
        collection {[string]} -- [Collection name where to add the face]
        image {[file]} -- [image to extract the face from]
        name {[type]} -- [identity UUID linked to the face]
    """
    with open(image_name, mode='rb') as file:
            response = client.index_faces(Image={'Bytes': file.read()}, CollectionId=collection, ExternalImageId=name, DetectionAttributes=['ALL'])
    print("name to put in database: ", name)

    i = Identities(uuid=name)
    db.session.add(i)
    db.session.flush()
    r = Represents(probability=100.0, fk_identity=i.id, fk_picture=picture.id)
    db.session.add(r)
    db.session.commit()

def handle_picture(picture_file, picture_name):
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_name)
        #get args
        collection = app.config['COLLECTION_NAME']

        #initialize reckognition sdk
        client = boto3.client('rekognition', aws_access_key_id=app.config['aws_access_key_id'],aws_secret_access_key=app.config['aws_secret_access_key'])

        face_matched, response = recognizeFace(client, picture_path , collection)
        p = Pictures(picPath=picture_name, timestamp=datetime.utcnow(), fk_place=1)
        db.session.add(p)
        db.session.flush()  
        print('Face detected!')
        if (face_matched):
            confidence = round(response['FaceMatches'][0]['Face']['Confidence'], 2)
            faceUUID = response['FaceMatches'][0]['Face']['ExternalImageId']
            similarity = round(response['FaceMatches'][0]['Similarity'], 1)
            foundIdentity = read_one_by_uuid(faceUUID)
            r = Represents(probability=confidence, fk_identity=foundIdentity.get('id'), fk_picture=p.id)
            db.session.add(r)
            db.session.flush()  
            print('Identity matched {} with {} similarity and {} confidence...'.format(faceUUID, similarity, confidence))
        else:
            print('Unknown Human Detected!')
            add_face_collection(collection, picture_path, str(uuid.uuid4()), client, p)
            time.sleep(5)
        db.session.commit()


