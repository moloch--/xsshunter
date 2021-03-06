# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

import re
import time

from datetime import datetime, timedelta
from hashlib import sha512
from os import urandom
from string import ascii_lowercase, digits
from time import time

import bcrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.twofactor import InvalidToken
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from sqlalchemy import Column
from sqlalchemy.orm import backref, relationship
from sqlalchemy.types import Boolean, DateTime, String, Text, Unicode
from sqlalchemy_utils import EncryptedType, URLType
from tornado.options import options

from models import DBSession
from models.base import DatabaseObject


class User(DatabaseObject):

    DOMAIN_CHARS = digits + ascii_lowercase
    LINUX_EPOCH = datetime(1970, 1, 1, 0, 0)
    MIN_PASSWORD_LENGTH = 1 if options.debug else 12

    OTP_LENGTH = 8
    OTP_STEP = 30
    OTP_ISSUER = "XSS-Hunter"

    FULL_NAME_LENGTH = 120
    _full_name = Column(Unicode(FULL_NAME_LENGTH))
    FULL_NAME_SCHEMA = {
        "type": "string",
        "minLength": 1,
        "maxLength": FULL_NAME_LENGTH
    }

    USERNAME_LENGTH = 80
    _username = Column(Unicode(USERNAME_LENGTH), unique=True, nullable=False)
    USERNAME_SCHEMA = {
        "type": "string",
        "minLength": 1,
        "maxLength": USERNAME_LENGTH
    }

    _password = Column(String(120))

    EMAIL_LENGTH = 120
    _email = Column(String(EMAIL_LENGTH), unique=True, nullable=False)
    EMAIL_SCHEMA = {
        "type": "string",
        "format": "email",
        "minLength": 1,
        "maxLength": EMAIL_LENGTH
    }

    DOMAIN_LENGTH = 32
    _domain = Column(String(DOMAIN_LENGTH), unique=True)
    DOMAIN_SCHEMA = {
        "type": "string",
        "maxLength": DOMAIN_LENGTH,
        "minLength": 1
    }

    _pgp_key = Column(Text())
    _chainload_uri = Column(URLType())
    email_enabled = Column(Boolean, default=False)
    _locked = Column(Boolean, default=False)
    _last_login = Column(DateTime)

    _otp_enabled = Column(Boolean, default=False)
    _otp_secret = Column(EncryptedType(String(128), options.database_secret))

    _password_reset_token_expires = Column(DateTime, default=LINUX_EPOCH)
    _password_reset_token = Column(String(128), nullable=False,
                                   default=lambda: urandom(32).encode('hex'))

    _api_key = Column(String(128), nullable=False,
                      default=lambda: urandom(32).encode('hex'))

    injections = relationship("InjectionRecord",
                              backref=backref("user", lazy="select"),
                              cascade="all,delete,delete-orphan")

    permissions = relationship("Permission",
                               backref=backref("user", lazy="select"),
                               cascade="all,delete,delete-orphan")

    @classmethod
    def by_domain(cls, domain):
        return DBSession().query(cls).filter_by(_domain=domain).first()

    @classmethod
    def by_username(cls, username):
        username = ''.join(username[:80].split())
        return DBSession().query(cls).filter_by(_username=username).first()

    @classmethod
    def by_api_key(cls, api_key):
        return DBSession().query(cls).filter_by(
            _api_key=sha512(api_key).digest()
        ).first()

    @staticmethod
    def hash_password(password, salt=None):
        """
        BCrypt has a max lenght of 72 chars, we first throw the plaintext thru
        SHA256 to support passwords greater than 72 chars.
        """
        if salt is None:
            salt = bcrypt.gensalt(10)
        return bcrypt.hashpw(sha512(password).digest(), salt)

    @property
    def permission_names(self):
        """ Return a list with all permissions accounts granted to the user """
        return [permission.name for permission in self.permissions]

    def has_permission(self, permission):
        """ Return True if 'permission' is in permissions_names """
        return True if permission in self.permission_names else False

    def compare_password(self, in_password):
        return self.hash_password(in_password, self.password) == self.password

    def generate_password_reset_token(self):
        """
        Generates a new password reset token and returns it, also save the new
        token as a hash in the database.
        """
        token = urandom(32).encode('hex')
        self._password_reset_token = sha512(token).hexdigest()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        self._password_reset_token_expires = expires_at
        return token

    def generate_api_key(self):
        token = urandom(32).encode('hex')
        self._api_key = sha512(token).hexdigest()
        return token

    def validate_password_reset_token(self, token):
        """
        You can't do a remote timing attack since we hash the input token, well
        unless you can generate lots of sha512 collisions, in which case you
        earned it buddy.
        """
        if datetime.utcnow() < self._password_reset_token_expires:
            if sha512(token).hexdigest() == self._password_reset_token:
                # Token can only be used once, override old value with garbage
                self._password_reset_token = urandom(32).encode('hex')
                self._password_reset_token_expires = User.LINUX_EPOCH
                return True
        return False

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, in_fullname):
        assert isinstance(in_fullname, basestring)
        self._full_name = in_fullname[:self.FULL_NAME_LENGTH].strip()

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, in_username):
        assert isinstance(in_username, basestring)
        self.username = ''.join(in_username.split())[:self.USERNAME_LENGTH]

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, in_password):
        if len(in_password) < self.MIN_PASSWORD_LENGTH:
            raise ValueError("Password must be %d+ chars" % (
                self.MIN_PASSWORD_LENGTH
            ))
        self._password = self.hash_password(in_password)

    @property
    def pgp_key(self):
        return self._pgp_key

    @pgp_key.setter
    def pgp_key(self, in_pgp_key):
        self._pgp_key = in_pgp_key

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, in_email):
        in_email = in_email.strip()

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, set_domain):
        assert isinstance(set_domain, basestring)

        if not 0 < len(set_domain) <= 32:
            raise ValueError("Invalid domain length")

        if any(char not in self.DOMAIN_CHARS for char in set_domain):
            raise ValueError("Invalid domain, domains can only contain %s" % (
                self.DOMAIN_CHARS
            ))

        # Check for duplicates
        if self.by_domain(set_domain) is not None:
            raise ValueError("Duplicate domain")
        else:
            self._domain = set_domain

    @property
    def last_login(self):
        return time.mktime(self._last_login.timetuple())

    @last_login.setter
    def last_login(self, value):
        self._last_login = value

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value):
        """ Lock account and revoke all API keys """
        assert isinstance(value, bool)
        if value:
            self._locked = True
            self._api_key = urandom(32).encode('hex')
        else:
            self._locked = False

    def validate_otp(self, value):
        """ Validate a one-time password """
        try:
            self._otp.verify(value.encode("ascii", "ignore"), time())
            return True
        except InvalidToken:
            return False

    @property
    def otp_enabled(self):
        return self._otp_enabled

    @otp_enabled.setter
    def otp_enabled(self, value):
        """
        Ensures that when 2fa is enabled/disabled we always use a fresh key
        """
        assert isinstance(value, bool)
        if value:
            self._otp_enabled = True
            self._otp_secret = urandom(64).encode('hex')
        else:
            self._otp_enabled = False
            self._otp_secret = ""

    @property
    def _otp(self):
        """
        Current one time password implementation, time-based "TOTP"
        https://cryptography.io/en/latest/hazmat/primitives/twofactor/
        """
        if not self._otp_enabled or len(self._otp_secret) < 1:
            raise ValueError("2FA/OTP is not enabled for this user")
        key = self._otp_secret.decode('hex')
        return TOTP(key, self.OTP_LENGTH, SHA512(), self.OTP_STEP,
                    backend=default_backend())

    @property
    def otp_provisioning_uri(self):
        """ Generate an enrollment URI for Authetnicator apps """
        return self._otp.get_provisioning_uri(self.username, self.OTP_ISSUER)

    def to_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "full_name": self.full_name,
            "email": self.email,
            "username": self.username,
            "pgp_key": self.pgp_key,
            "domain": self.domain,
            "email_enabled": self.email_enabled
        }

    def to_admin_dict(self):
        data = self.to_dict()
        data["updated"] = self.updated
        data["locked"] = self.locked
        data["last_login"] = self.last_login
        return data

    def __str__(self):
        return self.username + " - ( " + self.full_name + " )"
