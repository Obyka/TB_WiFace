import connexion
import config
import mariage
import os
from flask import abort, make_response, request, jsonify, render_template, redirect
from werkzeug.utils import secure_filename
from recognize_face import handle_picture
import probes
import macs
import identities
import belongsto
import pictures
import users
from dateutil.relativedelta import relativedelta
from flask_jwt_extended import get_jwt_identity, jwt_optional, jwt_required, get_raw_jwt
import datetime
from models import User, UserSchema
# Get the application instance
connex_app = config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('swagger.yml')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

@config.jwtM.unauthorized_loader
def unauthorized_loader_handler(error):
    if request.path.startswith('/api/'):
        return jsonify(err="missing JWT"), 401
    else:
        return redirect('/web/login')

@connex_app.app.context_processor
@jwt_optional
def inject_identity():
	return dict(identity=get_jwt_identity())

@connex_app.app.context_processor
def inject_counters():
    return dict(probe_count=probes.count(), mac_count=macs.count(), id_count=identities.count(), pic_cout=pictures.count(), mac_random=macs.count_random())

@connex_app.app.context_processor
def inject_path():
    return dict(picture_path=config.app.config['UPLOAD_FOLDER'])

@connex_app.route('/web/login', methods=['GET', 'POST'])
@jwt_optional
def login_front():
	identity = get_jwt_identity()
	print(str(identity)*100)
	if identity is not None:
		return redirect('/web/statistics')

	if request.method == 'POST':
		user = {'email': request.form['email'], 'password': request.form['password']}
		response =  users.login(user)
		if response.status_code != 200:
			return render_template('login.html', error=True, csrf_token=(get_raw_jwt() or {}).get("csrf"))
		else:
			# Since the login function returns a response, here is a convoluted way to copy tokens while serving a template
			r = make_response(render_template('login.html'))
			r.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
			return r
	return render_template('login.html', csrf_token=(get_raw_jwt() or {}).get("csrf"))

@connex_app.route('/web/statistics')
def statistics_front():
	test = pictures.feed()
	test = [((verbose_timedelta(datetime.datetime.utcnow() - i[0])), i[1]) for i in test]
	return render_template('statistics.html', message=mariage.mariage(), test=test)

@connex_app.route('/web/identities')
def identities_front():
	if 'id' in request.args:
		identity = identities.read_one(request.args.get('id'))
		macs = belongsto.read_by_identity(identity.get('id'))
		best_pic = pictures.read_best_pic(identity.get('id'))
		best_macs = mariage.best_fit(macs)
		best_pic_path = os.path.join(config.app.config['UPLOAD_FOLDER'], best_pic['picPath'])
		return render_template('identity_details.html', identity=identity, best_pic=best_pic_path, best_macs=best_macs)
	identitiy_list = identities.read_all()
	return render_template('identities.html', identitiy_list=identitiy_list)

@connex_app.route('/web/macs')
def macs_front():
	if 'id' in request.args:
		mac_data = macs.get_mac_infos(macs.read_one(request.args.get('id')))
		return render_template('mac_details.html', mac_data=mac_data)
	mac_list = macs.read_all()
	for mac in mac_list:
		mac =  macs.get_mac_infos(mac)
	return render_template('macs.html', mac_list=mac_list)

@connex_app.route('/web/pictures')
def pictures_front():
	return render_template('pictures.html')

def verbose_timedelta(delta):
    d = delta.days
    h, s = divmod(delta.seconds, 3600)
    m, s = divmod(s, 60)
    labels = ['day', 'hour', 'minute', 'second']   
    dhms = ['%s %s%s' % (i, lbl, 's' if i != 1 else '') for i, lbl in zip([d, h, m, s], labels)]
    for start in range(len(dhms)):
        if not dhms[start].startswith('0'):
            break
    for end in range(len(dhms)-1, -1, -1):
        if not dhms[end].startswith('0'):
            break  
    return ', '.join(dhms[start:end+1])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@connex_app.route('/api/upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(config.app.config['UPLOAD_FOLDER'], filename))
		handle_picture(file, filename)
		resp = jsonify({'message' : 'File successfully uploaded'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
	connex_app.run(host='0.0.0.0', port=5000, debug=True)


