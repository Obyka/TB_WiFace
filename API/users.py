from config import db
from models import User, UserSchema
from flask import abort, make_response, Response, jsonify
from flask_jwt_extended import set_refresh_cookies, unset_jwt_cookies, set_access_cookies, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt

@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200

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
        status_code = Response(status=404)
        return status_code
    else:
        if User.verifyHash(user.password, userDB.password):
            resp = jsonify({'login':True})     
            access_token = create_access_token(identity = user.email)
            refresh_token = create_refresh_token(identity = user.email)
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp        
        else:
            status_code = Response(status=401)
        return status_code
