# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2016
"""


import qrcode

from base64 import b64encode
from cStringIO import StringIO
from handlers.base import APIBaseHandler
from libs.json_api import json_api_method, BAD_REQUEST, PRIMARY_ID
from libs.decorators import authenticated
from libs.decorators import authorized
from libs.validation_errors import ValidationError
from models.permission import ADMIN_PERMISSION, Permission
from models.user import User


class MeAPIHandler(APIBaseHandler):

    @authenticated
    @json_api_method(None)
    def get(self):
        """
        Returns the current user's settings (email/etc)
        Ignore the Backbone.js ID values, and use the session.
        """
        user = self.get_current_user()
        self.write(user.to_dict())

    @authenticated
    @json_api_method({
        "type": "object",
        "properties": {
            "email_address": {"type": "string", "format": "email"},
            "email_updates": {"type": "boolean"},
            "new_password": {"type": "string"},
            "old_password": {"type": "string"}
        }
    })
    def put(self):
        """
        This function edit's the current user's settings (email/password/etc)
        Ignore the Backbone.js ID values, and use the session.
        """
        user = self.get_current_user()
        new_password = self.get_argument("new_password", "")
        old_password = self.get_argument("old_password", "")
        if len(new_password):
            if user.validate_password(old_password):
                user.password = new_password
            else:
                raise ValidationError("Old password is not valid")
        email_address = self.get_argument("email_address", "")
        if user.email_address != email_address:
            user.email_address = email_address
        self.dbsession.add(user)
        self.dbsession.commit()
        self.write(user.to_dict())


class OTPEnrollmentAPIHandler(APIBaseHandler):

    """ This handler manages a user 2FA/OTP settings """

    @authenticated
    @json_api_method({
        "type": "object",
        "properties": {}
    })
    def post(self):
        """ Enable OTP for the current user """
        user = self.get_current_user()
        if not user.otp_enabled:
            user.otp_enabled = True
            self.dbsession.add(user)
            self.dbsession.commit()
            user = self.get_current_user()  # Get the commit'd changes
            qr_image = qrcode.make(user.otp_provisioning_uri)
            data = StringIO()
            qr_image.save(data)
            data.seek(0)
            data_uri = "data:image/jpeg;base64,%s" % b64encode(data.read())
            self.write({
                "qrcode": data_uri,
                "uri": user.otp_provisioning_uri
            })
        else:
            self.write({"errors": ["OTP already enabled"]})

    @authenticated
    @json_api_method({
        "type": "object",
        "properties": {
            "enrollment": {"type": "string"},
            "otp": {"type": "string", "minLength": 8}
        },
        "required": ["otp"]
    })
    def put(self):
        """ Test an OTP code """
        user = self.get_current_user()
        otp = self.get_argument("otp", "")
        valid = user.validate_otp(otp)
        if not valid:
            self.set_status(BAD_REQUEST)
        self.write({"valid": valid})

    @authenticated
    @json_api_method({
        "type": "object",
        "properties": {
            "enrollment": {"type": "string"},
            "otp": {"type": "string", "minLength": 8}
        },
        "required": ["otp"]
    })
    def delete(self):
        """ Disable OTP for the current user, requires a valid/existing OTP """
        pass


###################################################################
#                      ADMIN ONLY HANDLERS
###################################################################
class AccountLockAPIHandler(APIBaseHandler):

    """ ADMIN-only controller used to lock user accounts """

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @json_api_method({
        "type": "object",
        "properties": {
            "user_id": PRIMARY_ID,
            "lock": {"type": "boolean"}
        },
        "required": ["user_id", "lock"]
    })
    def post(self):
        lock_user = User.by_id(self.get_argument('user_id', ''))
        if lock_user is not None and lock_user != self.get_current_user():
            lock_user.account_locked = bool(self.get_argument('lock', False))
            self.dbsession.add(lock_user)
            self.dbsession.commit()
            self.write(lock_user.to_admin_dict())
        else:
            self.set_status(BAD_REQUEST)
            self.write({'error': 'Invalid user'})


class UsersAPIHandler(APIBaseHandler):

    """
    ADMIN users only, managers have their own API endpoint for adding accounts to their own Team
    """

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @json_api_method(None)
    def get(self, user_id=""):
        """ Ignore the Backbone.js ID values, and use the session """
        user = self.get_current_user()
        if len(user_id) < 1:
            self.write([_user.to_admin_dict() for _user in User.all()])
        else:
            _user = User.by_id(user_id)
            if _user is not None:
                self.write(_user.to_admin_dict())
            else:
                raise ValidationError("User not found")

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @json_api_method({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email_address": {"type": "string"},
            "password": {"type": "string"},
            "confirm_password": {"type": "string"},
            "is_admin": {"type": "boolean"},
        },
        "required": ["name", "email_address", "password"]
    })
    def post(self, user_id=''):
        """ Create a new user account, on the current users's team """
        name = self.get_argument("name", "")
        email = self.get_argument("email_address", "")
        password = self.get_argument("password", "")
        is_admin = self.get_argument("is_admin", False)
        new_user = self.create_user(name, email, password, is_admin)
        self.write(new_user.to_admin_dict())

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @json_api_method({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "user_id": {"type": "string"},
            "email_address": {"type": "string"},
            "password": {"type": "string"},
            "confirm_password": {"type": "string"},
            "is_admin": {"type": "boolean"}
        },
        "required": ["name", "email_address", "password"]
    })
    def put(self, user_id=""):
        user = self.get_current_user()

        ch_user = User.by_id(user_id)
        if ch_user is None:
            raise ValidationError("Invalid user")

        username = self.get_argument("name", ch_user.name)
        if ch_user.name != username:
            ch_user.name = username

        email_address = self.get_argument("email_address", "")
        if ch_user.email_address != email_address:
            ch_user.email_address = email_address

        password = self.get_argument("password", "")
        if len(password):
            ch_user.password = password

        if self.get_argument("is_admin", False) and not ch_user.has_permission(ADMIN_PERMISSION):
            self._make_admin(ch_user)
        elif ch_user.has_permission(ADMIN_PERMISSION) and not self.get_argument("is_admin", False):
            self._remove_admin(ch_user)

        self.dbsession.add(ch_user)
        self.dbsession.commit()
        self.write(ch_user.to_admin_dict())

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @json_api_method(None)
    def delete(self, user_id=""):
        """ Delete an existing user """
        rm_user = User.by_id(user_id)
        if rm_user is not None and rm_user != self.get_current_user():
            self.dbsession.delete(rm_user)
            self.dbsession.commit()
            self.write({})
        elif rm_user == self.get_current_user():
            raise ValidationError("You cannot delete yourself")
        else:
            raise ValidationError("User not found")

    def create_user(self, username, email_address, password, is_admin):
        """ Create a new user """
        user = self.get_current_user()
        new_user = User(
            name=username[:User.USERNAME_LENGTH],
            password=password)
        # Next we set optional fields
        if 4 < len(email_address):
            new_user.email = email_address

        if is_admin:
            self._make_admin(new_user)

        # Commit it all to the DB
        self.dbsession.add(new_user)
        self.dbsession.commit()
        return new_user

    def _make_admin(self, user):
        """ Give a user ADMIN permission """
        admin_permission = Permission(name=ADMIN_PERMISSION, user_id=user.id)
        user.permissions.append(admin_permission)
        self.dbsession.add(admin_permission)

    def _remove_admin(self, user):
        permission = Permission.by_user_and_name(user, ADMIN_PERMISSION)
        self.dbsession.delete(permission)
        self.dbsession.commit()
