import os

import connexion
from dateutil.relativedelta import relativedelta
from flask import jsonify, make_response, redirect, request
from flask_jwt_extended import (get_jwt_identity, get_raw_jwt, jwt_optional,
                                jwt_required, unset_access_cookies,
                                unset_jwt_cookies)
from werkzeug.utils import secure_filename

import config
import users
from recognize_face import handle_picture
from web import web

# Get the application instance
connex_app = config.connex_app

connex_app.app.register_blueprint(web.web_bp, url_prefix='/web')

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('swagger.yml')


@config.jwtM.unauthorized_loader
def unauthorized_loader_handler(error):
    print("unauthorized token" * 1000)
    if request.path.startswith('/api/'):
        return jsonify(err="missing JWT"), 401
    else:
        return redirect('/web/login')


@config.jwtM.invalid_token_loader
def invalid_token_callback(callback):
    print("invalid token" * 1000)
    # Invalid Fresh/Non-Fresh Access token in auth header
    if request.path.startswith('/api/'):
        resp = make_response(jsonify(err="invalid JWT"))
    else:
        resp = make_response(redirect('/web/login'))
    unset_jwt_cookies(resp)
    return resp, 301


@config.jwtM.expired_token_loader
def expired_token_callback(callback):
    # Expired auth header
    print("expired token" * 10)
    response = users.refresh()
    resp = make_response(redirect(request.url))
    unset_access_cookies(resp)
    resp.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
    return resp, 301


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    connex_app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
