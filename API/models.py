from datetime import datetime

from passlib.hash import pbkdf2_sha256

from config import db, ma

class Probes(db.Model):
    __tablename__ = "probes"
    id = db.Column(db.Integer, primary_key=True)
    ssid = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fk_place = db.Column(db.Integer, db.ForeignKey('places.id'))
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
    def __str__(self):
        return self.fk_mac +" "+ str(self.fk_identity) + " " + str(self.probability) + "\n"

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
    belongsTo = db.relationship('BelongsTo', backref='mac', cascade="save-update, merge, delete")
    PP2I = db.Column(db.Boolean)

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
    represents = db.relationship('Represents', backref='identity', cascade="save-update, merge, delete")
    belongsTo = db.relationship('BelongsTo', backref='identity', cascade="save-update, merge, delete")
    PP2I = db.Column(db.Boolean)


class IdentitiesSchema(ma.ModelSchema):
    class Meta:
        model = Identities
        sqla_session = db.session

class Pictures(db.Model):
    __tablename__ = "pictures"
    id = db.Column(db.Integer, primary_key=True)
    picPath = db.Column(db.String(128))
    timestamp =  db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    eyeglasses = db.Column(db.Numeric(1,10))
    sunglasses = db.Column(db.Numeric(1,10))
    gender = db.Column(db.Numeric(1,10))
    beard = db.Column(db.Numeric(1,10))
    mustache = db.Column(db.Numeric(1,10))
    ageMin = db.Column(db.Integer)
    ageMax = db.Column(db.Integer)
    calm = db.Column(db.Numeric(1,10))
    sad = db.Column(db.Numeric(1,10))
    surprised = db.Column(db.Numeric(1,10))
    angry = db.Column(db.Numeric(1,10))
    happy = db.Column(db.Numeric(1,10))
    confused = db.Column(db.Numeric(1,10))
    fear = db.Column(db.Numeric(1,10))
    disgusted = db.Column(db.Numeric(1,10))
    brightness = db.Column(db.Numeric(1,10))
    sharpness = db.Column(db.Numeric(1,10))
    face_id = db.Column(db.String(36), unique=True)

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
    probes = db.relationship('Probes', backref='place')

class PlacesSchema(ma.ModelSchema):
    class Meta:
        model = Places
        sqla_session = db.session
        include_fk = True

class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    fk_place = db.Column(db.Integer, db.ForeignKey('places.id'))

    def __init__(self, email, password, admin, fk_place):
        self.email = email
        self.password = password
        self.admin = admin
        self.fk_place = fk_place
    
    @staticmethod
    def hash(password):
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verifyHash(password, hash):
        return pbkdf2_sha256.verify(password, hash)
    
class UserSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = User
        sqla_session = db.session