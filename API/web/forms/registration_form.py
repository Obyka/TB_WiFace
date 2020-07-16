from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, DecimalField, HiddenField,validators
from markupsafe import Markup
from wtforms.widgets.core import html_params
from wtforms.validators import ValidationError
from wtforms.csrf.session import SessionCSRF
from flask import session
from config import app

class CustomSelect:
    """
    Renders a select field allowing custom attributes for options.
    Expects the field to be an iterable object of Option fields.
    The render function accepts a dictionary of option ids ("{field_id}-{option_index}")
    which contain a dictionary of attributes to be passed to the option.

    Example:
    form.customselect(option_attr={"customselect-0": {"disabled": ""} })
    """

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, option_attr=None, **kwargs):
        if option_attr is None:
            option_attr = {}
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        html = ["<select %s>" % html_params(name=field.name, **kwargs)]
        for option in field:
            attr = option_attr.get(option.id, {})
            html.append(option(**attr))
        html.append("</select>")
        return Markup("".join(html))

class RegistrationForm(Form):
    email = StringField('Email', [validators.InputRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.EqualTo('confirm_password', message='Passwords must match'), validators.Length(min=4, max=35)])
    confirm_password = PasswordField('Confirm password', [])
    admin = BooleanField('Admin?', [])
    location = SelectField(u'Client location', coerce=int, widget=CustomSelect())
    new_location_name = StringField('New location name', [])
    longitude = DecimalField('Longitude',[validators.NumberRange(min=-180, max=180)], places=None)
    latitude = DecimalField('Latitude',[validators.NumberRange(min=-90, max=90)], places=None)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.location.data == -1 and (len(self.new_location_name.data) < 4 or len(self.new_location_name.data) > 40):
            self.new_location_name.errors.append('The place name must be filled.')
            return False
        return True

    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['CSRF_SECRET_KEY']

        @property
        def csrf_context(self):
            return session



