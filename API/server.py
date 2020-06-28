import connexion
import config
import os
from flask import make_response, request, jsonify, redirect
from werkzeug.utils import secure_filename
from recognize_face import handle_picture
import users
from dateutil.relativedelta import relativedelta
from flask_jwt_extended import get_jwt_identity, jwt_optional, jwt_required, get_raw_jwt, unset_access_cookies, unset_jwt_cookies

# Get the application instance
connex_app = config.connex_app

from web import web
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
	print("expired token" * 1000)
	response =  users.refresh()
	resp = make_response(request.url)
	unset_access_cookies(resp)    
	resp.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
	return resp, 302

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
	connex_app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))


