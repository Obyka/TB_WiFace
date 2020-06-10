from flask import render_template
import connexion
import config
import mariage
import os
from flask import abort, make_response, request, jsonify
from werkzeug.utils import secure_filename
from recognize_face import handle_picture
import probes
import macs
import identities
import belongsto
import pictures
import vendors
from dateutil.relativedelta import relativedelta
import datetime

# Get the application instance
connex_app = config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('swagger.yml')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@connex_app.app.context_processor
def inject_counters():
    return dict(probe_count=probes.count(), mac_count=macs.count(), id_count=identities.count(), pic_cout=pictures.count(), mac_random=macs.count_random())

@connex_app.app.context_processor
def inject_path():
    return dict(picture_path=config.app.config['UPLOAD_FOLDER'])

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
	mac_list = macs.read_all()
	for mac in mac_list:
		vendor = vendors.read_by_oui(mac['fk_vendor'])
		mac['vendor_name'] = vendor['name']
		mac['nb_probes'] = len(mac['probes'])

	return render_template('macs.html', mac_list=mac_list)

@connex_app.route('/web/pictures')
def pictures_front():
	return render_template('pictures.html')



ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

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


