from config import db
from models import User, UserSchema
from flask import abort, make_response, Response

def create(user):
    schema = UserSchema()
    new_user = schema.load(user, session=db.session)

    userDB = User.query \
        .filter(User.email==new_user.email) \
        .one_or_none()

    if userDB is not None:
        abort(409, 'user {email} already exist'.format(email=new_user.email))

    db.session.add(new_user)
    db.session.commit()
    status_code = Response(status=201)
    return status_code

def login(user):
    schema = UserSchema()
    user = schema.load(user, session=db.session)
    userDB = User.query\
        .filter(User.email==user.email).one_or_none()

    if userDB is None:
        abort(404, "User {email} does not exist".format(email=user.email))

    else:
        if user.password == userDB.password:
            return "GG t'es loggé", 200
        else:
            print(user.password, " ", userDB.password)
            abort(401, 'bad auth')
