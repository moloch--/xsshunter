
import json
import os
from datetime import datetime, timedelta

from tornado.options import options

from handlers.base import BaseHandler
from libs.decorators import json_api
from libs.mixins import SendEmailMixin
from models.user import User
from modles import DBSession


class LoginHandler(BaseHandler):

    @json_api({
        "type": "object",
        "properites": {
            "username": {"type": "string"},
            "password": {"type": "string"}
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
            return
        elif user.compare_password(req.get("password", "")):
            self.start_session(user)
            self.logit("Someone logged in as " + req["username"])
            return
        else:
            self.error("Invalid username or password supplied")

    def start_session(self, user):
        csrf_token = os.urandom(50).encode('hex')
        self.set_secure_cookie("session", json.dumps({
            "user": user.id,
            "expires": str(datetime.utcnow() + timedelta(days=1))
        }), secure=True)
        self.set_secure_cookie("csrf", csrf_token, secure=True)
        self.write(json.dumps({
            "success": True,
            "csrf_token": csrf_token,
        }))


class RegisterHandler(BaseHandler):

    MIN_PASSWORD_LENGTH = 1 if options.debug else 12

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
        if len(password) < self.MIN_PASSWORD_LENGTH:
            self.write({
                "success": False,
                "invalid_fields": ["password too short"]
            })
            return

        # add the new user to the database
        new_user = User(username=username, domain=domain, password=password)
        DBSession().add(new_user)
        DBSession().commit()
        self.logit("New user successfully registered with username of %r" % (
            req["username"]
        ))
        self.write({"success": True})


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
        self.clear_cookie("user")
        self.clear_cookie("csrf")
        self.redirect("/")
