from datetime import datetime
from config import db, ma


class Probes(db.Model):
    __tablename__ = "probes"
    id = db.Column(db.Integer, primary_key=True)
    ssid = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fk_place = db.Column(db.Integer)
    fk_mac = db.Column(db.String(18), db.ForeignKey('macAddress.address'))

class ProbesSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = Probes
        sqla_session = db.session

class Vendors(db.Model):
    __tablename__ = "vendors"
    oui = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

class VendorsSchema(ma.ModelSchema):
    class Meta:
        model = Vendors
        sqla_session = db.session

class MacAddress(db.Model):
    __tablename__ = "macAddress"
    address = db.Column(db.String(18), primary_key=True)
    isRandom = db.Column(db.Boolean)
    fk_vendor = db.Column(db.Integer)
    probes = db.relationship('Probes', backref='mac')


class MacAddressSchema(ma.ModelSchema):
    class Meta:
        model = MacAddress
        sqla_session = db.session

""" class GoesAlong(db.Model):
    __tablename__ = "goesAlong"
    probability = db.Column(db.Integer)
class GoesAlongSchema(ma.ModelSchema):
    class Meta:
        model = GoesAlong
        sqla_session = db.session """