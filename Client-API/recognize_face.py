from picamera import PiCamera
import cv2 as cv
import argparse
import time
from datetime import datetime, timedelta
import os
import uuid
from API import API, APIErrorNotFound
from Identity import Identity, Represents
from Picture import Picture
from Auth import User


creds = User("Obyka","pass")
MyAPI = API(creds, "http://localhost:5000/api/")

def detectFace(frame,face_cascade):
    """OpenCV face detection using pre-trained cascade
    
    Arguments:
        frame {[file]} -- [image which may contain a face]
        face_cascade {[file]} -- [pre-trained cascade to detect face]
    
    Returns:
        [face_detected] -- [Does the image contain a face?]
        [string] -- [Path of the saved image]
    """  
    face_detected = False
    faces = face_cascade.detectMultiScale(frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags = cv.CASCADE_SCALE_IMAGE)
    print("Found {0} faces!".format(len(faces)))
    timestr = time.strftime("%Y%m%d-%H%M%S")
    if len(faces) > 0 :
            face_detected = True

    return face_detected
def main():
    f = open("test.jpg", "rb")
    MyAPI.postPicture(f)
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

    
    while True:
            frame = {}
            #calling read() twice as a workaround to clear the buffer.
            cam.read()
            cam.read()
            ret, frame = cam.read()         
            if frame is None:
                    print('--(!) No captured frame -- Break!')
                    break

            face_detected = detectFace(frame,face_cascade)

            if (face_detected):
                    MyAPI.postPicture(frame)

            if cv.waitKey(20) & 0xFF == ord('q'):
                    break

    # When everything done, release the capture
    cam.release()
    cv.destroyAllWindows()

main()
