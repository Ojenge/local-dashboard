# -*- coding: utf-8 -*-

from datetime import timedelta, datetime

from Crypto import Random
from Crypto.Protocol import KDF

from sqlalchemy.orm.exc import NoResultFound

from local_api import db
from .schema import Validator


LOG = __import__('logging').getLogger('sqlalchemy')
HASH_ROUNDS = 1000
EXPIRY_HOURS = 24
DK_LEN = 32

def generate_password_hash(raw_password):
    """Generates a password for a user.

    The value will be stored in the database as a concatenation
    of a random salt and generated hash, separated by a full colon.

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
    d = datetime.utcnow() + timedelta(hours=EXPIRY_HOURS)
    LOG.error("Generated expiry: %r", d)
    return d

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
    password_changed = db.Column(db.Boolean,
                                 default=False)

    def set_password(self, password):
        pass_hash = generate_password_hash(password)
        self.password_hash = pass_hash

    def is_authenticated(self):
        return self.login is not None

    def is_active(self):
        return self.login is not None

    def is_anonymous(self):
        return self.login is None

    def get_id(self):
        return unicode(self.login)

    def __repr__(self):
        return '<User:%s>' % (self.login)



class AuthToken(db.Model):
    """Authentication token associated with a user.
    """

    def __init__(self, **kwargs):
        super(AuthToken, self).__init__(**kwargs)
        self.generate_token()

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), nullable=False, index=True, unique=True)
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


def create_user(login, password):
    """Create a user record
    :return: bool
    """
    completed = False
    try:
        user = Principal(login=login, password=password)
        db.session.add(user)
        db.session.commit()
        completed = True
    except Exception as exc:
        LOG.error('user creation failed: %s : %r', login, exc)
    return completed


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
    except NoResultFound:
        LOG.error("User not found with login: %s", login)
        # simulate a password check anyway
        KDF.PBKDF2(password, 'salt', dkLen=DK_LEN, count=HASH_ROUNDS).encode('hex')
    return is_verified


def change_password(payload, user_id):
    """Changes the user password
    :return: tuple
    """
    v = Validator(payload)
    v.ensure_exists('current_password')
    v.ensure_exists('password')
    v.ensure_equal('password', 'password_confirmation')
    v.ensure_format('password', r'^[\w@#.\+\-\*&%$]{5,32}$',
                    message=('password must be between 5 and 32 characters '
                             'and include any of these characters: letters, numbers and [@ # . + - * & % $]'))
    v.ensure_not_equal('password', 'current_password')
    if v.is_valid:
        check = check_password(user_id, payload['current_password'])
        if check:
            user = db.session.query(Principal).filter_by(login=user_id).one()
            user.set_password(payload['password'])
            user.password_changed = True
            db.session.add(user)
            db.session.commit()
            return (200, 'OK')
        else:
            v.add_error('password', 'current password does not match')
            return (422, v.errors)
    else:
        return (422, v.errors)

def check_header(auth_key):
    """Load the current user from authentication token
    :return: Principal|None
    """
    _user = None
    try:
        token  = db.session.query(AuthToken).filter_by(token=auth_key).one()
        # TODO: Handle proper expiry
        _user = token.principal
        if token.expiry > datetime.utcnow():
            _user = token.principal
        else:
            LOG.error('Token with id: %r is expired', token.id)
    except NoResultFound:
        LOG.error("Token not found:")
    return _user


def make_token(login):
    """Generate authentication token.

    :return: dict
    """
    auth_token = AuthToken(principal_id=login)
    db.session.add(auth_token)
    db.session.commit()
    return dict(token=auth_token.token,
                expiry=auth_token.expiry.isoformat(),
                password_changed=bool(auth_token.principal.password_changed))