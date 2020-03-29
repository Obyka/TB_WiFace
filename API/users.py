from config import db
from models import User, UserSchema
from flask import abort, make_response, Response
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

@jwt_required
def create(user):
    schema = UserSchema()
    new_user = schema.load(user, session=db.session)
    new_user.password = User.hash(new_user.password)

    userDB = User.query \
        .filter(User.email==new_user.email) \
        .one_or_none()

    if userDB is not None:
        abort(409, 'user {email} already exist'.format(email=new_user.email))

    db.session.add(new_user)
    db.session.commit()
    status_code = Response(status=201)

    access_token = create_access_token(identity = new_user.email)
    refresh_token = create_refresh_token(identity = new_user.email)

    return access_token, 201

def login(user):
    schema = UserSchema()
    user = schema.load(user, session=db.session)
    userDB = User.query\
        .filter(User.email==user.email).one_or_none()

    if userDB is None:
        abort(404, "User {email} does not exist".format(email=user.email))

    else:
        if User.verifyHash(user.password, userDB.password):
            access_token = create_access_token(identity = user.email)
            refresh_token = create_refresh_token(identity = user.email)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            abort(401, 'bad auth')
