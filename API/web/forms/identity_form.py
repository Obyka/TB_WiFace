from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import ValidationError
from wtforms.csrf.session import SessionCSRF
from config import app
from flask import request, session
class IdentityForm(Form):
    firstname = StringField('Firstname', [validators.InputRequired(), validators.Length(min=4, max=40)])
    lastname = StringField('Lastname', [validators.InputRequired(), validators.Length(min=4, max=40)])
    email = StringField('Email', [validators.InputRequired(), validators.Length(min=4, max=40)])

    class Meta:
            csrf = True
            csrf_class = SessionCSRF
            csrf_secret = app.config['CSRF_SECRET_KEY']

            @property
            def csrf_context(self):
                return session