#from picamera import PiCamera
import argparse
import os
import time
from datetime import datetime, timedelta

import cv2 as cv

from API import API, APIErrorNotFound
from Auth import User
from Identity import Identity, Represents
from Picture import Picture

def process_frame(frame, MyAPI):
    """Given a frame, this function will call all the cascades on it and flip it
    for the profile one. Then it sends the result to the API. 

    Args:
        frame: picture to process
        MyAPI (API): API object to use to send the results
    """
    base_cascade_path = cv.data.haarcascades
    face_cascade_list = [
        os.path.join(base_cascade_path, 'haarcascade_frontalface_alt2.xml'),
        os.path.join(base_cascade_path, 'haarcascade_frontalface_alt_tree.xml'),
        os.path.join(base_cascade_path, 'haarcascade_frontalface_alt.xml'),
        os.path.join(base_cascade_path, 'haarcascade_frontalface_default.xml'),
        os.path.join(base_cascade_path, 'haarcascade_profileface.xml')
    ]

    for x in face_cascade_list:
        if(detectFace(frame, x)):
            image = '{0}/image_{1}_complete.png'.format(directory, time.strftime("%Y%m%d-%H%M%S"))
            cv.imwrite(image, frame)
            MyAPI.postFile(image)
            return 

        if "haarcascade_profileface" in x:
            flipped_frame = cv.flip(frame, 1)
            if(detectFace(flipped_frame, x)):
                image = '{0}/image_{1}_complete.png'.format(directory, time.strftime("%Y%m%d-%H%M%S"))
                cv.imwrite(image, frame)
                MyAPI.postFile(image)
                return 
    

def TestWithoutOpenCV(image_path, MyAPI):
    """This function allows to send an image without OpenCV processing

    Args:
        image_path (string): the path of the image to send
        MyAPI (API): API instance to use the post method
    """
    MyAPI.postFile(image_path)


def detectFace(frame, cascade):
    """OpenCV face detection using pre-trained cascade

    Arguments:
        frame (file) -- [image which may contain a face]
        cascade (string) -- [path to pre-trained cascade to detect face]

    Returns:
        (face_detected) -- [Does the image contain a face?]
        (string) -- [Path of the saved image]
    """

    timestr = time.strftime("%Y%m%d-%H%M%S")
    image_list = []

    face_cascade = cv.CascadeClassifier()

    # Load the cascades
    if not face_cascade.load(cv.samples.findFile(cascade)):
        print('--(!)Error loading face cascade ' + str(cascade))
        return image_list

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,
                                            scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(30, 30),
                                            flags=cv.CASCADE_SCALE_IMAGE)
    print("Found {0} faces!".format(len(faces)) + " - " + str(cascade))

    return len(faces) > 0


def main():
    # get args
    parser = argparse.ArgumentParser(description='Facial recognition')
    parser.add_argument('--camera', help='Camera device number.', type=int, default=0)
    parser.add_argument('--api', help='Base address for the API')
    parser.add_argument('--frame', help='Picture path if you do not want to use the cam')
    parser.add_argument(
        '--debug', help='Boolean if you want to send hardcoded picture to test the server handling', action='store_true')

    args = parser.parse_args()
    username = os.environ['wiface_username']
    password = os.environ['wiface_password']
    creds = User(username, password)
    MyAPI = API(creds, args.api)


    if args.debug and args.frame is not None:
        TestWithoutOpenCV(args.frame, MyAPI)
        return

    if args.frame is not None:
        frame = cv.imread(args.frame)
        process_frame(frame, MyAPI)
        
    else:
        camera_device = args.camera
        # Read the video stream
        cam = cv.VideoCapture(camera_device)
        # setting the buffer size and frames per second, to reduce frames in buffer
        cam.set(cv.CAP_PROP_BUFFERSIZE, 1)
        cam.set(cv.CAP_PROP_FPS, 2)

        if not cam.isOpened:
            print('--(!)Error opening video capture')
            exit(0)

        while True:
            frame = {}
            # calling read() twice as a workaround to clear the buffer.
            cam.read()
            cam.read()
            ret, frame = cam.read()
            if frame is None:
                print('--(!) No captured frame -- Break!')
                break

            process_frame(frame, MyAPI)


        # When everything done, release the capture
        cam.release()
        cv.destroyAllWindows()


dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'faces')
main()
