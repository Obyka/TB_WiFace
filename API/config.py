import os
import connexion
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from os import environ





basedir = os.path.abspath(os.path.dirname(__file__))

# Create the connexion application instance
connex_app = connexion.App(__name__, specification_dir=basedir)

# Get the underlying Flask app instance
app = connex_app.app

# Build the Sqlite ULR for SqlAlchemy
sqlite_url = "sqlite:////" + os.path.join(basedir, "probes.db")

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = "static/images"
app.config['COLLECTION_NAME'] = "wiface-faces"
app.config['aws_access_key_id'] = "***REMOVED***"
app.config['aws_secret_access_key'] = "***REMOVED***"

app.config['SECRET_KEY'] = '***REMOVED***'

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

# Tokens for auth
jwtM = JWTManager(app)

def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
            dbapi_con.execute('pragma foreign_keys=ON')

with app.app_context():
    from sqlalchemy import event
    event.listen(db.engine, 'connect', _fk_pragma_on_connect)