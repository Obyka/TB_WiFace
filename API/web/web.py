import datetime
import os

from dateutil.relativedelta import relativedelta
from flask import (Blueprint, abort, make_response, redirect, render_template,
                   request)
from flask_jwt_extended import (get_jwt_identity, get_raw_jwt, jwt_optional,
                                jwt_required, unset_access_cookies,
                                unset_jwt_cookies)

import belongsto
import config
import identities
import macs
import mariage
import pictures
import probes
import users

# Blueprint Configuration
web_bp = Blueprint('web_bp', __name__, template_folder='templates', static_folder='static')

@web_bp.context_processor
@jwt_optional
def inject_identity():
	return dict(current_user=get_jwt_identity())

@web_bp.context_processor
def inject_counters():
	return dict(probe_count=probes.count(), mac_count=macs.count(), id_count=identities.count(), pic_cout=pictures.count(), mac_random=macs.count_random())

@web_bp.context_processor
def inject_path():
	return dict(picture_path=config.app.config['UPLOAD_FOLDER'])

@web_bp.route('/logout', methods=['GET', 'POST'])
@jwt_optional
def logout_front():
	response =  users.logout()
	# Since the login function returns a response, here is a convoluted way to copy tokens while serving a template
	r = redirect('/web/login')
	r.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
	return r

@web_bp.route('/login', methods=['GET', 'POST'])
@jwt_optional
def login_front():
	identity = get_jwt_identity()
	if identity is not None:
		return redirect('/web/statistics')

	if request.method == 'POST':
		user = {'email': request.form['email'], 'password': request.form['password']}
		response =  users.login(user)
		if response.status_code != 200:
			return render_template('login.html', error=True)
		else:
			# Since the login function returns a response, here is a convoluted way to copy tokens while serving a template
			r = redirect('/web/statistics')
			r.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
			return r
	return render_template('login.html', csrf_token=(get_raw_jwt() or {}).get("csrf"))

@web_bp.route('/statistics')
@jwt_required
def statistics_front():
	test = pictures.feed()
	test = [((verbose_timedelta(datetime.datetime.utcnow() - i[0])), i[1]) for i in test]
	return render_template('statistics.html', message=mariage.mariage(), test=test)

@web_bp.route('/identities')
@jwt_required
def identities_front():
	if 'id' in request.args:
		identity = identities.read_one(request.args.get('id'))
		macs = belongsto.read_by_identity(identity.get('id'))
		age_range = identities.read_age_range(identity.get('id'))
		gender_result = identities.read_gender(identity.get('id'))
		best_pic = pictures.read_best_pic(identity.get('id'))
		
		best_macs = mariage.best_fit(macs) if macs else []
		
		best_pic_path = best_pic['picPath']
		print(best_pic_path + ' ' * 1000)
		return render_template('identity_details.html', age_range=age_range,identity=identity, best_pic=best_pic_path, best_macs=best_macs, gender=gender_result)
	identitiy_list = identities.read_all()
	return render_template('identities.html', identitiy_list=identitiy_list)

@web_bp.route('/macs')
@jwt_required
def macs_front():
	if 'id' in request.args:
		mac_data = macs.get_mac_infos(macs.read_one(request.args.get('id')))
		return render_template('mac_details.html', mac_data=mac_data)
	mac_list = macs.read_all()
	for mac in mac_list:
		mac =  macs.get_mac_infos(mac)
	return render_template('macs.html', mac_list=mac_list)

@web_bp.route('/pictures')
@jwt_required
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
