# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

import re
from datetime import datetime, timedelta
from hashlib import sha256
from os import urandom
from time import time
from string import digits, ascii_lowercase

import bcrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.twofactor import InvalidToken
from furl import furl
from sqlalchemy import Column
from sqlalchemy.orm import backref, relationship
from sqlalchemy.types import Boolean, DateTime, String, Unicode, Text
from sqlalchemy_utils import URLType, EncryptedType
from tornado.options import options

from models import DBSession
from models.base import DatabaseObject


class User(DatabaseObject):

    DOMAIN_CHARS = digits + ascii_lowercase
    EMAIL_REGEX = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
    LINUX_EPOCH = datetime(1970, 1, 1, 0, 0)
    MIN_PASSWORD_LENGTH = 1 if options.debug else 12

    OTP_LENGTH = 8
    OTP_STEP = 30
    OTP_ISSUER = "XSS Hunter"

    _full_name = Column(Unicode(120))
    _username = Column(Unicode(80))
    _password = Column(String(120))
    _email = Column(String(120))
    _domain = Column(String(32), unqiue=True)
    _pgp_key = Column(Text())
    _chainload_uri = Column(URLType())
    email_enabled = Column(Boolean, default=False)
    _locked = Column(Boolean, default=False)
    last_login = Column(DateTime)

    _otp_enabled = Column(Boolean, default=False)
    _otp_secret = Column(EncryptedType(String(128), options.database_secret))

    _password_reset_token_expires = Column(DateTime, default=LINUX_EPOCH)
    _password_reset_token = Column(String(64), nullable=False,
                                   default=lambda: urandom(32).encode('hex'))

    _api_key = Column(String(64), nullable=False,
                      default=lambda: urandom(32).encode('hex'))

    injections = relationship("InjectionRecord",
                              backref=backref("user", lazy="select"),
                              cascade="all,delete,delete-orphan")

    collected_pages = relationship("CollectedPage",
                                   backref=backref("user", lazy="select"),
                                   cascade="all,delete,delete-orphan")

    permissions = relationship("Permission",
                               backref=backref("user", lazy="select"),
                               cascade="all,delete,delete-orphan")

    # Done this way to allow users to just paste and share relative page lists
    _page_collection_paths_list = Column(Text())

    @classmethod
    def by_domain(cls, domain):
        return DBSession().query(cls).filter_by(_domain=domain).first()

    @classmethod
    def by_username(cls, username):
        username = username[:80].strip()
        return DBSession().query(cls).filter_by(_username=username).first()

    @classmethod
    def by_api_key(cls, api_key):
        return DBSession().query(cls).filter_by(
            _api_key=sha256(api_key).hexdigest()
        ).first()

    @staticmethod
    def hash_password(password, salt=None):
        """
        BCrypt has a max lenght of 72 chars, we first throw the plaintext thru
        SHA256 to support passwords greater than 72 chars.
        """
        if salt is None:
            salt = bcrypt.gensalt(10)
        return bcrypt.hashpw(sha256(password).hexdigest(), salt)

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
        self._password_reset_token = sha256(token).hexdigest()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        self._password_reset_token_expires = expires_at
        return token

    def generate_api_key(self):
        token = urandom(32).encode('hex')
        self._api_key = sha256(token).hexdigest()
        return token

    def validate_password_reset_token(self, token):
        """
        You can't do a remote timing attack since we hash the input token, well
        unless you can generate lots of SHA256 collisions, in which case you
        earned it buddy.
        """
        if datetime.utcnow() < self._password_reset_token_expries:
            if sha256(token).hexdigest() == self._password_reset_token:
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
        self._full_name = in_fullname[:120].strip()

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, in_username):
        assert isinstance(in_username, basestring)
        self.username = in_username[:80].strip()

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
        if re.search(self.EMAIL_REGEX, in_email, flags=0):
            self._email = in_email
        else:
            raise ValueError("Not a valid email")

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
    def chainload_uri(self):
        return self._chainload_uri

    @chainload_uri.setter
    def chainload_uri(self, in_chainload_uri):
        """ I've tightend this down to just HTTP/HTTPS Urls """
        if len(in_chainload_uri) <= 3:
            raise ValueError("URI too short")
        malicious_url = furl(in_chainload_uri)
        if malicious_url.scheme in ["http", "https"] and malicious_url.host:
            self._chainload_uri = malicious_url
        else:
            raise ValueError("URI scheme must be http/https")

    @property
    def page_collection_paths_list(self):
        if self.page_collection_paths_list is None:
            return []
        lines = self.page_collection_paths_list.split("\n")
        page_list = [line.strip() for line in lines]
        return filter(lambda line: line != "", page_list)

    @page_collection_paths_list.setter
    def page_collection_paths_list(self, in_paths_list_text):
        self._page_collection_paths_list = in_paths_list_text.strip()

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
        return self._otp.get_provisioning_uri(self.name, self.OTP_ISSUER)

    def to_dict(self):
        return {
            "id": self.id,
            "created": str(self.created),
            "full_name": self.full_name,
            "email": self.email,
            "username": self.username,
            "pgp_key": self.pgp_key,
            "domain": self.domain,
            "email_enabled": self.email_enabled,
            "chainload_uri": str(self.chainload_uri),
        }

    def to_admin_dict(self):
        data = self.to_dict()
        data["updated"] = str(self.updated)
        data["locked"] = self.locked
        data["last_login"] = str(self.last_login)
        return data

    def __str__(self):
        return self.username + " - ( " + self.full_name + " )"
