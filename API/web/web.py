import datetime
import os
from functools import wraps

from models import (Identities, IdentitiesSchema)
from dateutil.relativedelta import relativedelta
from flask import (Blueprint, abort, make_response, redirect, render_template,
                   request, jsonify)
from flask_jwt_extended import (verify_jwt_in_request, get_jwt_identity, get_jwt_claims, get_raw_jwt, jwt_optional,
                                jwt_required, unset_access_cookies,
                                unset_jwt_cookies)

import belongsto
import config
import identities
import macs
import json
import mariage
import pictures
import probes
import users
import avatar
import places
from .forms.registration_form import RegistrationForm
from .forms.login_form import LoginForm
from .forms.mac_addresses_form import MACAddressForm 
from .forms.identity_form import IdentityForm 
from wtforms import BooleanField
from werkzeug.exceptions import HTTPException

# Blueprint Configuration
web_bp = Blueprint('web_bp', __name__, template_folder='templates', static_folder='static')
# Here is a custom decorator that verifies the JWT is present in
# the request, as well as insuring that this user has a role of
# `admin` in the access token
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims['admin']:
            return jsonify(msg='Admins only!'), 403
        else:
            return fn(*args, **kwargs)
    return wrapper

@web_bp.context_processor
@jwt_optional
def inject_identity():
	return dict(current_user=get_jwt_identity(), current_role=get_jwt_claims())

@web_bp.context_processor
def inject_path():
	return dict(picture_path=config.app.config['UPLOAD_FOLDER'])

@web_bp.route('/places/<place_id>', methods=['GET'])
@admin_required
def place_front(place_id):
	place_data = places.get_place_infos(places.read_one(place_id))
	return render_template('place_details.html', place=place_data)

@web_bp.route('/places')
@admin_required
def places_front():
	places_list = places.read_all()
	return render_template('places.html', places_list=places_list)

@web_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register_front():
	all_places = places.read_all()

	form = RegistrationForm(request.form)
	form.location.choices = [(place.get('id'), place.get('name')) for place in all_places]
	form.location.choices.append((-1, "New place"))
	attribute_places = {"location-"+str(i):{"latitude":place.get('latitude'), "longitude":place.get('longitude')} for i,place in enumerate(all_places)}

	if request.method == 'POST':
		if form.validate():
			location = form.location.data
			# We will create a new place
			if form.location.data == -1:
				place = {"name": form.new_location_name.data, "longitude": form.longitude.data, "latitude": form.latitude.data}
				response, status_code = places.create(place)
				if status_code == 409:
					error = 'Place {place} already exist'.format(place=place.get('name'))
					return render_template('register.html' ,register_form=form,error=error,attribute_places=attribute_places)
				if status_code == 201:
					location = response['id']
			user = {'email': form.email.data, 'password': form.password.data, 'admin': form.admin.data, 'fk_place': location}		
			response =  users.create(user)
			if response.status_code == 409:
				error = 'User {email} already exist'.format(email=request.form['email'])
				return render_template('register.html' ,register_form=form,error=error,attribute_places=attribute_places)
			elif response.status_code != 201:
				error = "An unexpected error has occurred. Please try again later"
				return render_template('register.html', register_form=form,error=error,attribute_places=attribute_places)
			else:
				return render_template('register.html', register_form=form,success=True,attribute_places=attribute_places)
		else:
			return render_template('register.html',register_form=form, form_error=form.errors,attribute_places=attribute_places)
	else:
		form.location.data = -1
		return render_template('register.html', register_form=form, attribute_places=attribute_places)

@web_bp.route('/logout', methods=['GET', 'POST'])
@jwt_optional
def logout_front():
	response =  users.logout()
	# Since the login function returns a response, here is a convoluted way to copy tokens while serving a template
	r = redirect('/web/login')
	r.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
	return r

@web_bp.route('/login', methods=['GET', 'POST'])
def login_front():
	login_form = LoginForm(request.form)
	identity = get_jwt_identity()
	if identity is not None:
		return redirect('/web/statistics')

	if request.method == 'POST':
		if login_form.validate():
			user = {'email': request.form['email'], 'password': request.form['password']}
			response =  users.login(user)
			if response.status_code != 200:
				error = "Wrong credentials"
				return render_template('login.html', login_form=login_form, error=error)
			else:
				# Since the login function returns a response, here is a convoluted way to copy tokens while serving a template
				r = redirect('/web/statistics')
				r.headers.setlist('Set-Cookie', response.headers.getlist('Set-Cookie'))
				return r
		else:
			return render_template('login.html', login_form=login_form, form_error=login_form.errors)
	return render_template('login.html', login_form=login_form)

@web_bp.route('/pp2i', methods=['PUT'])
@admin_required
def pp2i_front():
	mariage.mariage()
	return ('', 204)

@web_bp.route('/statistics')
@admin_required
def statistics_front():
	feed = [((verbose_timedelta(datetime.datetime.now() - i[0])), i[1]) for i in pictures.feed()]
	return render_template('statistics.html', feed=feed, probe_count=probes.count(), mac_count=macs.count(), id_count=identities.count(), pic_cout=pictures.count(), mac_random=macs.count_random())

@web_bp.route('/represents/<represent_id>', methods=['GET'])
@admin_required
def represents_front(represent_id):
		identity = identities.read_one(represent_id)
		represents_datas = identities.read_pictures(identity.get('id'))
		pictures_list = []
		for represents_data in represents_datas:
			pictures_list.append(pictures.read_one(represents_data.get('fk_picture')))
		return render_template('represents.html', pictures_list=pictures_list, identity=identity)

@web_bp.route('/identities/<identity_id>', methods=['GET', 'POST', 'DELETE'])
def identity_form_front(identity_id):
	if request.method == "GET":
		identity_form = IdentityForm()
		identity = identities.read_one(identity_id)
		nb_picture = pictures.count_by_id(identity.get('id'))
		mac_addresses = belongsto.read_by_identity(identity.get('id'))
		age_range = identities.read_age_range(identity.get('id'))
		gender_result = identities.read_gender(identity.get('id'))
		best_pic = pictures.read_best_pic(identity.get('id'))[0]
		pictures_place = pictures.get_picture_place_by_identity(identity.get('id'))
		avatar_path = avatar.draw_avatar(best_pic)
		best_macs = mariage.best_fit(mac_addresses) if mac_addresses else []
		mac_datas = []
		for mac in best_macs:
			mac_datas.append(macs.get_mac_infos(macs.read_one(mac.get('fk_mac'))))
		return render_template('identity_details.html',identity_form=identity_form, pictures_place=pictures_place, nb_picture=nb_picture, age_range=age_range,identity=identity, best_pic=best_pic, best_macs=best_macs, gender=gender_result, mac_datas=mac_datas,avatar_path=avatar_path)

	if request.method == "DELETE":
		try:
			identities.delete(identity_id)
		except HTTPException:
			return '', 404
		return '', 204

	if request.method == "POST":
		form = IdentityForm(request.form)
		schema = IdentitiesSchema()
		if form.csrf_token.validate(IdentityForm):
			old_identity = identities.read_one(identity_id)
			old_identity = schema.load(old_identity)
			old_identity.mail=form.email.data if form.email.validate(IdentityForm) else old_identity.mail
			old_identity.firstname=form.firstname.data if form.firstname.validate(IdentityForm) else old_identity.firstname
			old_identity.lastname=form.lastname.data if form.lastname.validate(IdentityForm) else old_identity.lastname
			serialized_identity=schema.dump(old_identity)
			identities.edit_identity(identity_id, serialized_identity)
			return jsonify({'firstname': old_identity.firstname, 'lastname':old_identity.lastname, 'mail':old_identity.mail}), 201
		else:
			return '', 500
@web_bp.route('/identities', methods=['GET', 'POST'])
@admin_required
def identities_front():
	identitiy_list = identities.read_all()
	if request.method == 'POST':
		for identity in identitiy_list:
			new_PP2I = str(identity['id']) in request.form
			if new_PP2I != identity['PP2I']:
				identities.edit_pp2i(identity['id'], new_PP2I)
		return redirect('/web/identities')
	return render_template('identities.html', identitiy_list=identitiy_list)

@web_bp.route('/macs/<mac_id>', methods=['GET', 'DELETE'])
@admin_required
def mac_front(mac_id):
	if request.method == "DELETE":
		try:
			macs.delete(mac_id)
		except HTTPException:
			return '', 404
		return '', 204
	if request.method == "GET":
		mac_data = macs.get_mac_infos(macs.read_one(mac_id))
		return render_template('mac_details.html', mac_data=mac_data)
@web_bp.route('/macs', methods=['GET', 'POST', 'DELETE'])
@admin_required
def macs_front():
	mac_list = macs.read_all()
	if request.method == 'POST':
		for mac in mac_list:
			new_PP2I = mac['address'] in request.form
			if new_PP2I != mac['PP2I']:
				macs.edit_pp2i(mac['address'], new_PP2I)
		return redirect('/web/macs')
	else:
		for mac in mac_list:
			mac =  macs.get_mac_infos(mac)
		return render_template('macs.html', mac_list=mac_list)

@web_bp.route('/pictures/<picture_id>', methods=['GET'])
@admin_required
def pictures_front(picture_id):
	emotions = ['happy', 'surprised', 'fear', 'confused', 'sad', 'calm', 'disgusted', 'angry']
	current_pic = pictures.read_one(picture_id)
	avatar_path = avatar.draw_avatar(current_pic)
	# retire les trois expressions principales de la photo et les trie
	main_emotions = sorted([(emotion, current_pic.get(emotion)) for count, emotion in enumerate(emotions) if current_pic.get(emotion) and abs(current_pic.get(emotion)) >= 10], key=lambda emotion: emotion[1], reverse=True)[:3]
	return render_template('pictures.html', current_pic=current_pic, main_emotions=main_emotions,avatar_path=avatar_path)


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
