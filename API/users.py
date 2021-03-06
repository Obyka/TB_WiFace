from flask import Response, abort, jsonify, make_response, redirect, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, get_raw_jwt,
                                jwt_refresh_token_required, jwt_required,
                                set_access_cookies, set_refresh_cookies,
                                unset_access_cookies, unset_jwt_cookies)

from config import db, jwtM
from models import User, UserSchema


@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_identity = get_jwt_identity()
    userDB = User.query\
        .filter(User.email == current_identity).one_or_none()

    access_token = create_access_token(identity=userDB)

    # Set the JWT access cookie in the response
    resp = make_response(jsonify({'refresh': True}), 200)
    set_access_cookies(resp, access_token)
    return resp


@jwt_required
def create(user):
    schema = UserSchema()
    new_user = schema.load(user, session=db.session)
    new_user.password = User.hash(new_user.password)
    userDB = User.query \
        .filter(User.email == new_user.email) \
        .one_or_none()

    if userDB is not None:
        return Response(status=409)
    db.session.add(new_user)
    db.session.commit()
    access_token = create_access_token(identity=new_user)
    refresh_token = create_refresh_token(identity=new_user)
    return Response(response=schema.dump(new_user), status=201, mimetype='application/json')


def login(user):
    userDB = User.query\
        .filter(User.email == user.get('email')).one_or_none()

    if userDB is None:
        status_code = Response(status=404)
        return status_code
    else:
        if User.verifyHash(user.get('password'), userDB.password):
            resp = jsonify({'login': True})
            access_token = create_access_token(identity=userDB)
            refresh_token = create_refresh_token(identity=userDB)
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp
        else:
            status_code = Response(status=401)
        return status_code


@jwt_required
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp
