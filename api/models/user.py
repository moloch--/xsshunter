# -*- coding: utf-8 -*-
"""
@author: moloch, mandatory
Copyright 2015
"""

import re
from datetime import datetime, timedelta
from hashlib import sha256
from os import urandom

import bcrypt
from furl import furl
from sqlalchemy import Column
from sqlalchemy.orm import backref, relationship
from sqlalchemy.types import Boolean, DateTime, String, Text
from sqlalchemy_utils import URLType
from tornado.options import options

from models import DBSession
from models.base import DatabaseObject


class User(DatabaseObject):

    EMAIL_REGEX = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
    DOMAIN_REGEX = r"^[a-z0-9]+$"
    LINUX_EPOCH = datetime(1970, 1, 1, 0, 0)
    MIN_PASSWORD_LENGTH = 1 if options.debug else 12

    _full_name = Column(String(120))
    _username = Column(String(80))
    _password = Column(String(120))
    _email = Column(String(120))
    _domain = Column(String(32), unqiue=True)
    _pgp_key = Column(Text())
    email_enabled = Column(Boolean, default=False)
    _chainload_uri = Column(URLType())

    _password_reset_token_expires = Column(DateTime, default=LINUX_EPOCH)
    _password_reset_token = Column(String(64), nullable=False,
                                   default=lambda: urandom(32).encode('hex'))

    owner_correlation_key = Column(String(64), nullable=False,
                                   default=lambda: urandom(32).encode('hex'))

    injections = relationship("InjectionRecord",
                              backref=backref("user", lazy="select"),
                              cascade="all,delete,delete-orphan")

    collected_pages = relationship("CollectedPage",
                                   backref=backref("user", lazy="select"),
                                   cascade="all,delete,delete-orphan")

    # Done this way to allow users to just paste and share relative page lists
    _page_collection_paths_list = Column(Text())

    @classmethod
    def by_domain(cls, domain):
        return DBSession().query(cls).filter_by(_domain=domain).first()

    @classmethod
    def by_username(cls, username):
        username = username[:80].strip().encode('ascii', 'ignore')
        return DBSession().query(cls).filter_by(_username=username).first()

    @classmethod
    def by_owner_correlation_key(cls, correlation_key):
        return DBSession().query(cls).filter_by(
            owner_correlation_key=correlation_key
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
        self._full_name = in_fullname[:120].strip().encode('ascii', 'ignore')

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, in_username):
        assert isinstance(in_username, basestring)
        self.username = in_username[:80].strip().encode('ascii', 'ignore')

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
        self._pgp_key = in_pgp_key.strip()

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
        # Convert to lower case and remove whitespace
        set_domain = ''.join(set_domain.lower().split())[:32]

        # Short-cut if domain is the same
        if self._domain == set_domain:
            return

        # Check for only valid characters
        if not re.search(self.DOMAIN_REGEX, set_domain, flags=0):
            raise ValueError("Invalid domain")

        # Check for duplicates
        if self.by_domain(set_domain) is not None:
            raise ValueError("Invalid domain")
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
            "owner_correlation_key": self.owner_correlation_key
        }

    def __str__(self):
        return self.username + " - ( " + self.full_name + " )"
