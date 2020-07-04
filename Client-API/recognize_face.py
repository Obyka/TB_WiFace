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

    image_list = []

    for x in face_cascade_list:
        image_list_faces, frame = detectFace(frame, x)
        image_list.extend(image_list_faces)

        if "haarcascade_profileface" in x:
            image_list_faces, frame = detectFace(frame, x)
            image_list.extend(image_list_faces)
    
    image = '{0}/image_{1}_complete.png'.format(directory, time.strftime("%Y%m%d-%H%M%S"))
    cv.imwrite(image, frame)

    for im in image_list:
        MyAPI.postFile(im)

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


    m = 0.2
    # Ici, on recouvre les tous les visages sauf 1 à chaque fois, et on enregistre l'image
    for it, _ in enumerate(faces):
        copy_frame = frame.copy()
        for i, (x, y, w, h) in enumerate(faces):
            start_y = int(max(0, y-m*h))
            end_y = int(min(y + h + m*h, frame.shape[0]))
            start_x = int(max(0, x-m*w))
            end_x = int(min(x + w + m*h, frame.shape[1]))

            if i != it:
                roi_color = copy_frame[start_y:end_y, start_x:end_x]
                cv.rectangle(copy_frame, (start_x, start_y),
                                (end_x, end_y), (0, 255, 0), -1)
        image = '{0}/image_{1}_{2}_{3}.png'.format(directory, timestr, i, it)
        cv.imwrite(image, copy_frame)
        image_list.append(image)
    
    # Ici, on recouvre les tous les visages trouvé par la cascade sur la frame originale
    for i, (x, y, w, h) in enumerate(faces):
        start_y = int(max(0, y-m*h))
        end_y = int(min(y + h + m*h, frame.shape[0]))
        start_x = int(max(0, x-m*w))
        end_x = int(min(x + w + m*h, frame.shape[1]))

        roi_color = frame[start_y:end_y, start_x:end_x]
        cv.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), -1)
    return image_list, frame


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
