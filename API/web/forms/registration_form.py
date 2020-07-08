from wtforms import Form, BooleanField, StringField, PasswordField, SelectField ,validators
from markupsafe import Markup
from wtforms.widgets.core import html_params
from wtforms.validators import ValidationError

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

def new_place_validator(form, field):
    if form.location.data == -1:
        validators.length(min=4, max=25)

class RegistrationForm(Form):
    email = StringField('Email', [validators.InputRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.InputRequired(), validators.Length(min=4, max=35)])
    confirm_password = PasswordField('Confirm password', [validators.InputRequired(), validators.Length(min=4, max=35)])
    admin = BooleanField('Admin?', [])
    location = SelectField(u'Client location', coerce=int, widget=CustomSelect())
    new_location_name = StringField('New location name', [new_place_validator])



