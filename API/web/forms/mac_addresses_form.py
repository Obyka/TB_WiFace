from wtforms import Form, validators, BooleanField, FieldList, FormField, SubmitField

class MACAddressForm(Form):
    """A form for one or more addresses"""
    submit = SubmitField("Submit")