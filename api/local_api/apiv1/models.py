# -*- coding: utf-8 -*-

from datetime import timedelta, datetime

from Crypto import Random
from Crypto.Protocol import KDF

from sqlalchemy.orm.exc import NoResultFound

from local_api import db


LOG = __import__('logging').getLogger('sqlalchemy')
HASH_ROUNDS = 20000
EXPIRY_HOURS = 1
DK_LEN = 32




def check_password(login, password):
    """Checks provided credentials against database.

    :return: tuple
    """
    is_verified = False
    try:
        user = db.session.query(Principal).filter_by(login=login).one()
        salt, pass_hash = user.password_hash.split(':')
        computed = KDF.PBKDF2(password, salt, dkLen=DK_LEN, count=HASH_ROUNDS).encode('hex')
        if computed == pass_hash:
            is_verified = True
    except NoResultFound as exc:
        LOG.error("User not found with login: %s", login)
        # simulate a password check anyway
        KDF.PBKDF2(password, 'salt', dkLen=DK_LEN, count=HASH_ROUNDS).encode('hex')
    return is_verified


def generate_password_hash(raw_password):
    """Generates a password for a user.

    The value will be stored in the database as a concatenation
    of a random salt and generated hash, separated by a comma.

    :return: string
    """
    rand = Random.new()
    salt = rand.read(64).encode('hex')
    pass_hash = KDF.PBKDF2(raw_password, salt, dkLen=DK_LEN, count=HASH_ROUNDS).encode('hex')
    return '%s:%s' %(salt, pass_hash)



def generate_expiry():
    """Generates expiry date for a token
    :return: datetime.datetime
    """
    return datetime.utcnow() + timedelta(hours=EXPIRY_HOURS)



class Principal(db.Model):
    """User DB Representation
    """

    def __init__(self, **kwargs):
        raw_password = kwargs.pop('password')
        super(Principal, self).__init__(**kwargs)
        if raw_password:
            self.set_password(raw_password)

    login = db.Column(db.String(64), primary_key=True)
    password_hash = db.Column(db.String(256),
                              nullable=False)
    created = db.Column(db.DateTime,
                        default=datetime.utcnow(),
                        nullable=False)
    updated = db.Column(db.DateTime,
                        default=db.func.now(),
                        onupdate=datetime.utcnow(),
                        nullable=False)

    def set_password(self, password):
        pass_hash = generate_password_hash(password)
        self.password_hash = pass_hash

    def __repr__(self):
        return '<User:%s>' % (self.login)



class AuthToken(db.Model):
    """Authentication token associated with a user.
    """

    def __init__(self, **kwargs):
        super(AuthToken, self).__init__(**kwargs)
        self.generate_token()

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    expiry = db.Column(db.DateTime, default=generate_expiry(), nullable=False)
    principal_id = db.Column(db.String, db.ForeignKey('principal.login'), nullable=False)
    principal = db.relationship('Principal',
                                backref=db.backref('auth_tokens', lazy=True))

    def generate_token(self):
        rand = Random.new()
        self.token = rand.read(64).encode('hex')


    def __repr__(self):
        return '<AuthToken:%s>' % (self.principal_id)