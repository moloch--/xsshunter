# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

import json
import os
from datetime import datetime, timedelta

from tornado.options import options

from furl import furl
from handlers.base import BaseHandler
from libs.decorators import json_api
from libs.mixins import SendEmailMixin
from models.user import User


class LoginHandler(BaseHandler):

    @json_api({
        "type": "object",
        "properites": {
            "username": {"type": "string"},
            "password": {"type": "string"},
            "otp": {"type": "string"}
        },
        "required": ["username", "password"]
    })
    def post(self, req):
        user = User.by_username(req.get("username", ""))
        if user is None:
            User.hash_password(req.get("username", ""))
            self.error("Invalid username or password supplied")
            self.logit("Someone failed to log in as  %r" % req["username"],
                       "warn")
        elif user.compare_password(req.get("password", "")):
            if user.otp_enabled:
                if user.validate_otp(req.get("otp", "")):
                    self.start_session(user)
                else:
                    self.error("Invalid otp supplied")
            else:
                self.start_session(user)
        else:
            self.error("Invalid username or password supplied")

    def start_session(self, user):
        csrf_token = os.urandom(50).encode('hex')
        user.last_login = datetime.utcnow()
        self.db_session.add(user)
        self.db_session.commit()
        self.set_secure_cookie("session", json.dumps({
            "user": user.id,
            "expires": str(datetime.utcnow() + timedelta(days=1))
        }), secure=True)
        self.set_secure_cookie("csrf", csrf_token, secure=True)
        self.write({
            "success": True
        })


class RegisterHandler(BaseHandler):

    @json_api({
        "type": "object",
        "properites": {
            "username": {"type": "string"},
            "password": {"type": "string"},
            "domain": {"type": "string"}
        },
        "required": ["username", "password", "domain"]
    })
    def post(self, req):
        username = req.get("username", "")
        if User.by_username(username):
            self.write({
                "success": False,
                "invalid_fields": ["username (already registered!)"],
            })

        domain = req.get("domain", "")
        if User.by_domain(domain):
            self.write({
                "success": False,
                "invalid_fields": ["domain (already registered!)"],
            })
            return

        password = req.get("password", "")
        if len(password) < User.MIN_PASSWORD_LENGTH:
            self.write({
                "success": False,
                "invalid_fields": ["password too short"]
            })
            return

        # add the new user to the database
        new_user = User(username=username, domain=domain, password=password)
        self.db_session.add(new_user)
        self.db_session.commit()
        self.logit("New user successfully registered with username of %r" % (
            req["username"]
        ))
        self.write({"success": True})


class RequestPasswordResetHandler(BaseHandler, SendEmailMixin):

    @json_api({
        "type": "object",
        "properties": {
            "username": {"type": "string"}
        },
        "required": ["username"]
    })
    def post(self, req):
        """
        There is a slight timing attack here, you could potentially detect if
        the system sent an email or not, but it's not really a big deal since
        our sign-up form also leaks usernames by design. We pass the token via
        a URI fragment to avoid it getting logged by the webserver.
        """
        user = User.by_username(req.get("username", ""))
        if user is not None:
            token = user.generate_password_reset_token()
            self.db_session.add(user)
            self.db_session.commit()
            reset_url = furl()
            reset_url.scheme = "https"
            reset_url.hostname = options.domain
            reset_url.path = "/password-reset"
            reset_url.fragment = token
            body = self.render_password_reset_email(user, str(reset_url))
            self.send_email(user.email, "Password Reset", body)
            del token  # Snake oil
        self.write({"success": True})

    def render_password_reset_email(self, user, url):
        pass  # TODO: Create a template


class PasswordResetHandler(BaseHandler):

    @json_api({
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password_reset_token": {"type": "string"},
            "new_password": {"type": "string"}
        },
        "required": ["username", "password_reset_token", "new_password"]
    })
    def post(self, req):
        user = User.by_username(req.get("username", ""))
        if user is not None:
            token = req.get("password_reset_token", "")
            if user.validate_password_reset_token(token):
                user.password = req.get("new_password", "")
                self.db_session.add(user)
                self.db_session.commit()
                self.write({"success": True})
        self.write({"success": False})


class ContactUsHandler(BaseHandler, SendEmailMixin):

    @json_api({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "email"},
            "body": {"type": "string"}
        },
        "required": ["name", "email", "body"]
    })
    def post(self, req):
        self.logit("Someone just used the 'Contact Us' form.")
        subject = "XSSHunter Contact Form Submission"
        email_body = "Name: " + req["name"] + "\n"
        email_body += "Email: " + req["email"] + "\n"
        email_body += "Message: " + req["body"] + "\n"
        self.send_email(options.abuse_email, subject, email_body)
        self.write({"success": True})


class HealthHandler(BaseHandler):

    def get(self):
        self.write({"status": "ok"})


class LogoutHandler(BaseHandler):

    def get(self):
        self.logit("User is logging out.")
        self.clear_cookie("session")
        self.clear_cookie("csrf")
        self.redirect("/")
