from datetime import datetime
from config import db, ma
from passlib.hash import pbkdf2_sha256

class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = password
        self.admin = admin
    
    @staticmethod
    def hash(password):
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verifyHash(password, hash):
        return pbkdf2_sha256.verify(password, hash)
    
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        sqla_session = db.session

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

class BelongsTo(db.Model):
    __tablename__ = "belongsTo"
    probability = db.Column(db.Integer)
    fk_mac = db.Column(db.String(18), db.ForeignKey('macAddress.address'))
    fk_identity = db.Column(db.Integer, db.ForeignKey('identities.id'))
    db.PrimaryKeyConstraint(fk_mac, fk_identity, name='belongsTo')

class BelongsToSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = BelongsTo
        sqla_session = db.session

class Represents(db.Model):
    __tablename__ = "represents"
    probability = db.Column(db.Float)
    fk_identity = db.Column(db.Integer, db.ForeignKey('identities.id'))
    fk_picture = db.Column(db.Integer, db.ForeignKey('pictures.id'))
    db.PrimaryKeyConstraint(fk_identity, fk_picture, name='represents_pk')

class RepresentsSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = Represents
        sqla_session = db.session

class MacAddress(db.Model):
    __tablename__ = "macAddress"
    address = db.Column(db.String(18), primary_key=True)
    isRandom = db.Column(db.Boolean)
    fk_vendor = db.Column(db.String(8), db.ForeignKey('vendors.oui'))
    probes = db.relationship('Probes', backref='mac')
    belongsTo = db.relationship('BelongsTo', backref='mac')

class MacAddressSchema(ma.ModelSchema):
    class Meta:
        model = MacAddress
        sqla_session = db.session
        include_fk = True

class Vendors(db.Model):
    __tablename__ = "vendors"
    oui = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(32))
    macs = db.relationship('MacAddress', backref='vendor')

class VendorsSchema(ma.ModelSchema):
    class Meta:
        model = Vendors
        sqla_session = db.session

class Identities(db.Model):
    __tablename__ = "identities"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True)
    firstname = db.Column(db.String(32))
    lastname = db.Column(db.String(32))
    mail = db.Column(db.String(64))
    represents = db.relationship('Represents', backref='identity')
    belongsTo = db.relationship('BelongsTo', backref='identity')


class IdentitiesSchema(ma.ModelSchema):
    class Meta:
        model = Identities
        sqla_session = db.session

class Pictures(db.Model):
    __tablename__ = "pictures"
    id = db.Column(db.Integer, primary_key=True)
    picPath = db.Column(db.String(128))
    timestamp =  db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fk_place = db.Column(db.Integer, db.ForeignKey('places.id'))
    Represents = db.relationship('Represents', backref='picture')


class PicturesSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = Pictures
        sqla_session = db.session

class Places(db.Model):
    __tablename__ = "places"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    pictures = db.relationship('Pictures', backref='place')

class PlacesSchema(ma.ModelSchema):
    class Meta:
        model = Places
        sqla_session = db.session
        include_fk = True

