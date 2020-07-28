import os

import connexion
from dateutil.relativedelta import relativedelta
from flask import jsonify, make_response, redirect, request, render_template
from flask_jwt_extended import (get_jwt_identity, get_raw_jwt, jwt_optional,
                                jwt_required, unset_access_cookies,
                                unset_jwt_cookies)
from werkzeug.utils import secure_filename

import config
import users
from web import web

# Get the application instance
connex_app = config.connex_app

connex_app.app.register_blueprint(web.web_bp, url_prefix='/web')

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('swagger.yml')
@config.app.errorhandler(404)
@config.app.errorhandler(405)
def _handle_api_error(ex):
    if request.path.startswith('/web/'):
        return render_template('404.html'), 404    
    else:
        return "Ressource not found.", 404
@config.app.errorhandler(500)
def handle_500(err):
    if request.path.startswith('/web/'):
        return render_template('500.html'), 500    
    else:
        return "Internal error", 404
    

@config.jwtM.user_claims_loader
def add_claims_to_access_token(user):
    return {'admin': user.admin, 'fk_place': user.fk_place}

@config.jwtM.user_identity_loader
def user_identity_lookup(user):
    return user.email

@config.jwtM.unauthorized_loader
def unauthorized_loader_handler(error):
    if request.path.startswith('/api/'):
        resp = make_response(jsonify(err="missing JWT"),401)
    else:
        resp = make_response(redirect('/web/login'))
    unset_jwt_cookies(resp)
    return resp

@config.jwtM.invalid_token_loader
def invalid_token_callback(callback):
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
    response = users.refresh()
    resp = make_response(redirect(request.url))
    unset_access_cookies(resp)
    resp.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
    return resp, 301


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    connex_app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=('cert.pem', 'key.pem'))
