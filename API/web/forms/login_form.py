from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import ValidationError

class LoginForm(Form):
    email = StringField('Email', [validators.InputRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Length(min=4, max=35)])



