import logging
import os
from os import environ


import connexion
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import boto3

basedir = os.path.abspath(os.path.dirname(__file__))

# Create the connexion application instance
connex_app = connexion.App(__name__, specification_dir=basedir)

# Get the underlying Flask app instance
app = connex_app.app


log = logging.getLogger('werkzeug')
log.disabled = False

# Build the Sqlite ULR for SqlAlchemy
sqlite_url = "sqlite:////" + os.path.join(basedir, "probes.db")

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = "web/static/images"
app.config['COLLECTION_NAME'] = "wiface-faces"
app.config['aws_access_key_id'] = "***REMOVED***"
app.config['aws_secret_access_key'] = "***REMOVED***"

app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['SECRET_KEY'] = '***REMOVED***'
app.config['CSRF_SECRET_KEY'] = b'***REMOVED***'
 
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_CSRF_CHECK_FORM'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 600

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

boto_client = boto3.client('rekognition', aws_access_key_id=app.config['aws_access_key_id'], aws_secret_access_key=app.config['aws_secret_access_key'], region_name='us-east-1')

# Initialize Marshmallow
ma = Marshmallow(app)

# Tokens for auth
jwtM = JWTManager(app)

def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
    dbapi_con.execute('pragma foreign_keys=ON')

with app.app_context():
    from sqlalchemy import event
    event.listen(db.engine, 'connect', _fk_pragma_on_connect)
