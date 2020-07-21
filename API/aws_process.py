import boto3
from PIL import Image, ImageOps
import json
import io
import os
from config import boto_client, app, db
from datetime import datetime, timedelta

from flask_jwt_extended import (jwt_required, get_jwt_claims)

import time
import uuid
import identities
from models import BelongsTo, Identities, Pictures, Places, Represents

aws_rekognition_client=boto_client

def delete_faces_from_collection(collection, faces, client):

    response=client.delete_faces(CollectionId=collection,
                               FaceIds=faces)
    
    return len(response['DeletedFaces'])

def add_face_collection(collection, image_name, face_identity, client):
    """Index the face contained in an image and add it in a collection

    Arguments:
        collection {[string]} -- [Collection name where to add the face]
        image {[file]} -- [image to extract the face from]
        name {[type]} -- [identity UUID linked to the face]
    """
    face_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    with open(face_path, mode='rb') as file:
        response = client.index_faces(Image={'Bytes': file.read()}, CollectionId=collection,
                                      ExternalImageId=face_identity.uuid, DetectionAttributes=['ALL'])
    return response

#This function request sends an image to Rekognition to detect faces in the image stored in S3
#Function returns a JSON object containing details about detected faces.
def detect_faces_from_image(sourceImage):
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], sourceImage)
    with open(picture_path, 'rb') as file:
        response = aws_rekognition_client.detect_faces(Image={'Bytes': file.read()})
    return response['FaceDetails']


#This function creates cropped images from an image with multiple faces based on detected faces returned by Rekognition
#It returns a list of names of those cropped images
def create_cropped_images_of_detected_faces(detected_faces,sourceImage, size_of_border, image_format):
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], sourceImage)
        try:
            img = Image.open(picture_path)
        except Exception as e:
            print('Error while opening the image')
        list_of_cropped_images=[]
        actual_image_width, actual_image_height = img.size
        for count_of_cropped_faces, face in enumerate(detected_faces):
            x = int(face['BoundingBox']['Left']*actual_image_width)
            height = int(face['BoundingBox']['Height']*actual_image_height)
            width = int(face['BoundingBox']['Width']*actual_image_width)
            y = int(face['BoundingBox']['Top']*actual_image_height)
            crop_rectangle = ( x, y, width+x, height+y )
            cropped_im = ImageOps.expand(img.crop(crop_rectangle), border=size_of_border)
            name_of_cropped_image = os.path.join("face_" + str(time.strftime("%Y%m%d-%H%M%S")) + str(count_of_cropped_faces)+ '.png')
            try:
                cropped_im.save(os.path.join(app.config['UPLOAD_FOLDER'], name_of_cropped_image), image_format)
            except Exception as e:
                print(e)
            list_of_cropped_images.append(name_of_cropped_image)
        return list_of_cropped_images

#Performs search of images using images on local drive against a collection of images
def search_rekognition_for_matching_faces(face_to_search_for, collectionId, face_match_threshold, maximum_faces, image_format):
    face_path = os.path.join(app.config['UPLOAD_FOLDER'], face_to_search_for)

    open_image = Image.open(face_path)
    stream = io.BytesIO()
    open_image.save(stream,format=image_format)
    image_binary = stream.getvalue()

    response = aws_rekognition_client.search_faces_by_image(CollectionId=collectionId,Image={'Bytes':image_binary},FaceMatchThreshold=face_match_threshold, MaxFaces=maximum_faces)
    return response

#This function prints the results of from a SearchByImage API call
def print_search_results(matched_faces, face_image_name):
    print("#----------------------------------------------#")
    if matched_faces:
            print ('MATCH FOUND for ' + face_image_name + ', with ATTRIBUTES: ' )
            for match in matched_faces:
                    print ('FaceId: ' + match['Face']['FaceId'])
                    print ('Confidence: '+ str(match['Face']['Confidence']))
                    print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                    print("#----------------------------------------------#")
                    print("")
    else:
            
            print(" NO MATCH FOUND for " + face_image_name)
            print("#----------------------------------------------#")
            print("")


def constructPictureObject(face_id, faceDetails, picture_name, fk_place):
    booleanAttr = ['Eyeglasses', 'Sunglasses', 'Beard', 'Mustache']
    parsedDict = dict()
    for attribute in booleanAttr:
        attributeDetails = faceDetails[attribute]
        parsedDict[attribute.lower()] = attributeDetails['Confidence'] if attributeDetails['Value'] else - \
            attributeDetails['Confidence']

    parsedDict['brightness'] = faceDetails['Quality']['Brightness']
    parsedDict['sharpness'] = faceDetails['Quality']['Sharpness']

    parsedDict['face_id'] = face_id
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

#This is the part that actually runs the functions to achieve the desired result
@jwt_required
def handle_picture(picture_name):
    # get args
    image_format = 'PNG'

    #Declare and initialize variables
    collection_id = app.config['COLLECTION_NAME']
    face_threshold_value = 80 # set percemtage o
    max_number_of_faces= 1 # limit number of matched faces returned
    size_of_border = 1 #Size of border around cropped image

    #Detect and return faces, reads image from S3
    try:
        detected_faces = detect_faces_from_image(picture_name)
    except Exception as e:
        print(e)
        return 0

    #Create cropped images and return list of there names, uses image in same location as script
    list_of_cropped_faces = create_cropped_images_of_detected_faces(
            detected_faces,
            picture_name, 
            size_of_border,
            image_format
            )

    nb_face_found = len(list_of_cropped_faces)
    for cropped_face in list_of_cropped_faces:
        #Search for each face in your collection of faces
        try:
            response_search = search_rekognition_for_matching_faces(
                cropped_face,
                collection_id,
                face_threshold_value,
                max_number_of_faces, 
                image_format
                )

        except boto_client.exceptions.InvalidParameterException as e:
            nb_face_found-=1
            continue

        if(response_search['FaceMatches']):
            confidence = round(response_search['FaceMatches'][0]['Face']['Confidence'], 2)
            faceUUID = response_search['FaceMatches'][0]['Face']['ExternalImageId']
            similarity = round(response_search['FaceMatches'][0]['Similarity'], 1)
            try:
                get_identity = identities.read_one_by_uuid(faceUUID)
            except Exception as e:
                continue
            face_identity = Identities(id=get_identity['id'], uuid=get_identity['uuid'])
        else:
            new_identity = True
            confidence = 100
            faceUUID = str(uuid.uuid4())
            face_identity = Identities(uuid=faceUUID)
            db.session.add(face_identity)
            db.session.flush()
        try:
            fullFaceResponse = add_face_collection(collection_id, cropped_face, face_identity, aws_rekognition_client)
        except Exception as e:
            print(e)
            continue
        if len(fullFaceResponse['FaceRecords']) == 0:
            if new_identity:
                db.session.delete(face_identity)
                db.session.flush()
            continue
        
        faceDetails = fullFaceResponse['FaceRecords'][0]['FaceDetail']
        face_id = fullFaceResponse['FaceRecords'][0]['Face']['FaceId']
        p = constructPictureObject(face_id, faceDetails, cropped_face, get_jwt_claims()['fk_place'])
        db.session.add(p)
        db.session.flush()
        r = Represents(probability=confidence, fk_identity=face_identity.id, fk_picture=p.id)
        db.session.add(r)
        db.session.flush()
        db.session.commit()

