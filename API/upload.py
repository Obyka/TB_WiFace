import os
import time

from dateutil.relativedelta import relativedelta
from flask import jsonify, redirect, request
from werkzeug.utils import secure_filename

import config
from recognize_face import handle_picture

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename('face_upload_%s.%s' % (time.strftime("%Y%m%d-%H%M%S"), file.filename.split('.')[-1]))
        # save data to file system
        complete_file_name = os.path.join(config.app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(complete_file_name))
        try:
            handle_picture(file, filename)
        except ValueError:
            os.remove(complete_file_name)
            resp = jsonify({'message': 'No face was found in the picture.'})
            resp.status_code = 500
            return resp
        except Exception:
            os.remove(complete_file_name)
            resp = jsonify({'message': 'An error occured while handling the picture'})
            resp.status_code = 500
            return resp

        resp = jsonify({'message': 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are ' + str(ALLOWED_EXTENSIONS)})
        resp.status_code = 400
        return resp