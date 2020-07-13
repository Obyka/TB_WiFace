from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import ValidationError
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta
from config import app
from flask import request, session
class LoginForm(Form):
    email = StringField('Email', [validators.InputRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Length(min=4, max=35)])

    class Meta:
            csrf = True
            csrf_class = SessionCSRF
            csrf_secret = app.config['CSRF_SECRET_KEY']

            @property
            def csrf_context(self):
                return session