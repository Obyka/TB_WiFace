from picamera import PiCamera
import cv2 as cv
import argparse
import boto3
import time
import os
import uuid
from API import API
from Identity import Identity, Represents
from Auth import User


creds = User("Obyka","pass")
MyAPI = API(creds)


def recognizeFace(client,image,collection):
        face_matched = False
        with open(image, 'rb') as file:
                response = client.search_faces_by_image(CollectionId=collection, Image={'Bytes': file.read()}, MaxFaces=1, FaceMatchThreshold=85)
                if (not response['FaceMatches']):
                    face_matched = False
                else:
                    face_matched = True
                return face_matched, response

def add_face_collection(collection, image, name=str(uuid.uuid4())):
        #initialize reckognition sdk
        client = boto3.client('rekognition')
        with open(image, mode='rb') as file:
                response = client.index_faces(Image={'Bytes': file.read()}, CollectionId=collection, ExternalImageId=name, DetectionAttributes=['ALL'])
                print(len(response))
        print("name to put in database: ", name)
        new_identity = Identity("", "", "", name)
        MyAPI.postIdentity(new_identity)

def detectFace(frame,face_cascade):     
        face_detected = False
        #Detect faces
        faces = face_cascade.detectMultiScale(frame,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags = cv.CASCADE_SCALE_IMAGE)
        print("Found {0} faces!".format(len(faces)))
        timestr = time.strftime("%Y%m%d-%H%M%S")
        image = '{0}/image_{1}.png'.format(directory, timestr)
        if len(faces) > 0 :
                face_detected = True
                cv.imwrite(image,frame) 
                print('Your image was saved to {}'.format(image))

        return face_detected, image
def main():
        #get args
        parser = argparse.ArgumentParser(description='Facial recognition')
        parser.add_argument('--collection', help='Collection Name', default='wiface-faces')
        parser.add_argument('--face_cascade', help='Path to face cascade.', default='/usr/local/lib/python3.7/dist-packages/cv2/data/haarcascade_frontalface_alt2.xml')
        parser.add_argument('--camera', help='Camera device number.', type=int, default=0)
        args = parser.parse_args()


        #intialize opencv face detection
        face_cascade_name = args.face_cascade
        face_cascade = cv.CascadeClassifier()

        #Load the cascades
        if not face_cascade.load(cv.samples.findFile(face_cascade_name)):
                print('--(!)Error loading face cascade')
                exit(0)

        camera_device = args.camera

        #Read the video stream
        cam = cv.VideoCapture(camera_device)
        #setting the buffer size and frames per second, to reduce frames in buffer
        cam.set(cv.CAP_PROP_BUFFERSIZE, 1)
        cam.set(cv.CAP_PROP_FPS, 2)

        if not cam.isOpened:
                print('--(!)Error opening video capture')
                exit(0)

        #initialize reckognition sdk
        client = boto3.client('rekognition')

        while True:
                frame = {}
                #calling read() twice as a workaround to clear the buffer.
                cam.read()
                cam.read()
                ret, frame = cam.read()         
                if frame is None:
                        print('--(!) No captured frame -- Break!')
                        break

                face_detected, image = detectFace(frame,face_cascade)

                if (face_detected):
                        face_matched, response = recognizeFace(client, image , args.collection)
                        print('Face detected!')
                        if (face_matched):
                            confidence = round(response['FaceMatches'][0]['Face']['Confidence'], 2)
                            print('Identity matched {} with {} similarity and {} confidence...'.format(response['FaceMatches'][0]['Face']['ExternalImageId'], round(response['FaceMatches'][0]['Similarity'], 1), confidence))
                                
                        else:
                            print('Unknown Human Detected!')
                            add_face_collection(args.collection, image)
                            time.sleep(5)

                if cv.waitKey(20) & 0xFF == ord('q'):
                        break

        # When everything done, release the capture
        cam.release()
        cv.destroyAllWindows()

dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'faces')
main()
