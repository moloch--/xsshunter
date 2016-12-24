# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

import json
import time
from datetime import datetime

from furl import furl
from tornado.log import app_log
from tornado.options import options

from handlers.base import APIBaseHandler
from libs.decorators import json_api
from libs.mixins import SendEmailMixin
from libs.validation_errors import ValidationError
from models.user import User


class BaseAuthenticationAPIHandler(APIBaseHandler):

    AUTHENTICATION_TYPE = "base"
    SESSION_EXPIRES = 3600 * 6

    def post(self):
        raise NotImplementedError()

    def login_success(self, user):
        """
        Create a session and return it to the client, sessions are *not*
        cookies, instead we use a an hmac'd JSON blob that we hand to
        the client. The client includes this hmac'd blob in a header
        `X-XSS-HUNTER` on all requests (including GETs).
        """
        app_log.info("Successful authentication request for %s", user.username)
        user.last_login = datetime.utcnow()
        self.dbsession.add(user)
        self.dbsession.commit()
        session = {
            'user_id': user.id,
            'expires': int(time.time()) + self.SESSION_EXPIRES,
        }
        session['ip_address'] = self.request.remote_ip
        secure_session = self.create_signed_value(name="session",
                                                  value=json.dumps(session))
        # We put some data in here so the client can know when the session
        # expires and what the user's name is, etc -but we never trust it.
        # Server-side we only trust values from the hmac'd session `data`
        resp = {
            "username": user.username,
            "password": None,
            "data": secure_session,
            "expires": int(session['expires']),
        }
        if options.debug:
            resp["debug"] = bool(options.debug)
        return resp

    def login_failure(self):
        """ Child class implements this """
        raise NotImplementedError()



class LoginHandler(BaseAuthenticationAPIHandler):

    """ Handles basic username/password logins """

    @json_api({
        "type": "object",
        "properites": {
            "username": User.USERNAME_SCHEMA,
            "password": {"type": "string"},
            "otp": {"type": "string"}
        },
        "required": ["username", "password"]
    })
    def post(self, req):
        user = User.by_username(self.get_argument("username", ""))

        if user is None:
            User.hash_password(self.get_argument("password", ""))
            app_log.warn("Someone failed to log in as  %r", req["username"])
            raise ValidationError("Invalid username or password supplied")
        otp_valid = user.validateOtp(self.get_argument("otp", "")) if user.opt_enabled else True
        if otp_valid and user.compare_password(self.get_argument("password", "")):
            self.login_success(user)
        else:
            raise ValidationError("Invalid username or password supplied")


class RegistrationHandler(APIBaseHandler):

    """ Creates a new user """

    @json_api({
        "type": "object",
        "properites": {
            "username": User.USERNAME_SCHEMA,
            "email": User.EMAIL_SCHEMA,
            "password": {
                "type": "string",
                "minLength": 1
            },
            "confirm_password": {"type": "string"},
            "domain": User.DOMAIN_SCHEMA,
            "recaptch": {"type": "string"}
        },
        "required": ["username", "email", "password", "domain"]
    })
    def post(self, req):
        username = self.get_argument("username", "")
        if User.by_username(username):
            raise ValidationError("Invalid username, already in use")

        domain = self.get_argument("domain", "")
        if User.by_domain(domain):
            raise ValidationError("Domain is already registered")

        email_address = self.get_argument("email", "")
        password = self.get_argument("password", "")

        # add the new user to the database
        new_user = User(username=username, email=email_address, domain=domain, password=password)
        self.dbsession.add(new_user)
        self.dbsession.commit()
        app_log.info("New user successfully registered with username of %r", req["username"])
        self.write(new_user.to_dict())


class RequestPasswordResetHandler(APIBaseHandler, SendEmailMixin):

    """ Handles password resets """

    @json_api({
        "type": "object",
        "properties": {
            "username": User.USERNAME_SCHEMA
        },
        "required": ["username"]
    })
    def post(self):
        """
        There is a slight timing attack here, you could potentially detect if
        the system sent an email or not, but it's not really a big deal since
        our sign-up form also leaks usernames by design. We pass the token via
        a URI fragment to avoid it getting logged by the webserver.
        """
        user = User.by_username(self.get_argument("username", ""))
        if user is not None:
            token = user.generate_password_reset_token()
            self.dbsession.add(user)
            self.dbsession.commit()
            reset_url = furl()
            reset_url.scheme = "https"
            reset_url.hostname = options.domain
            reset_url.path = "/password-reset"
            reset_url.fragment = token
            body = self.render_password_reset_email(user, str(reset_url))
            self.send_email(user.email, "Password Reset", body)
            del token  # Snake oil
        self.write({
            "success": True
        })

    def render_password_reset_email(self, user, url):
        pass  # TODO: Create a template


class PasswordResetHandler(APIBaseHandler):

    @json_api({
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password_reset_token": {"type": "string"},
            "new_password": {"type": "string"}
        },
        "required": ["username", "password_reset_token", "new_password"]
    })
    def post(self):
        user = User.by_username(self.get_argument("username", ""))
        if user is not None:
            token = self.get_argument("password_reset_token", "")
            if user.validate_password_reset_token(token):
                user.password = self.get_argument("new_password", "")
                self.dbsession.add(user)
                self.dbsession.commit()
                self.write({"success": True})
        self.write({"success": False})


class ContactUsHandler(APIBaseHandler, SendEmailMixin):

    @json_api({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "email"},
            "body": {"type": "string"}
        },
        "required": ["name", "email", "body"]
    })
    def post(self):
        app_log.info("Someone just used the 'Contact Us' form.")
        subject = "XSSHunter Contact Form Submission"
        email_body = "Name: " + self.get_argument("name", "") + "\n"
        email_body += "Email: " + self.get_argument("email", "") + "\n"
        email_body += "Message: " + self.get_argument("body", "") + "\n"
        self.send_email(options.abuse_email, subject, email_body)
        self.write({"success": True})


class HealthHandler(APIBaseHandler):

    def get(self):
        self.write({"status": "ok"})
