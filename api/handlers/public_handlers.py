
import json

from tornado import gen

from handlers.base import BaseHandler
from models.user import User


class LoginHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        req_data = json.loads(self.request.body)

        user = User.by_username(req_data.get("username", ""))

        if user is None:
            self.error("Invalid username or password supplied")
            self.logit("Someone failed to log in as " + user_data["username"], "warn")
            return
        elif user.compare_password(req_data.get("password", "")):
            self.start_session(user)
            self.logit("Someone logged in as " + user_data["username"])
            return
        self.error("Invalid username or password supplied")
        return

    def start_session(self, user):
        csrf_token = os.urandom(50).encode('hex')
        request_handler.set_secure_cookie("user", user.id, secure=True)
        request_handler.set_secure_cookie("csrf", csrf_token, secure=True)
        request_handler.write(json.dumps({
            "success": True,
            "csrf_token": csrf_token,
        }))


class RegisterHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        user_data = json.loads(self.request.body)
        user_data["email_enabled"] = True

        if User.by_username(user_data.get("username", "")):
            already_exists = {
                "success": False,
                "invalid_fields": ["username (already registered!)"],
            }
            self.write(already_exists)

        domain = user_data.get("domain", "")
        if User.by_domain(domain) or domain in FORBIDDEN_SUBDOMAINS:
            domain_exists = {
                "success": False,
                "invalid_fields": ["domain (already registered!)"],
            }
            self.write(domain_exists)
            return

        new_user = User()

        return_dict = {}
        allowed_attributes = ["pgp_key", "full_name", "domain", "email",
                              "password", "username", "email_enabled"]
        invalid_attribute_list = []
        for key, value in user_data.iteritems():
            if key in allowed_attributes:
                return_data = new_user.set_attribute(key, user_data.get(key))
                if return_data is not True:
                    invalid_attribute_list.append(key)

        new_user.generate_user_id()

        if invalid_attribute_list:
            return_dict["success"] = False
            return_dict["invalid_fields"] = invalid_attribute_list
            return_dict = {
                "success": False,
                "invalid_fields": ["username (already registered!)"],
            }
            self.write(json.dumps(return_dict))
            return

        self.logit("New user successfully registered with username of " + user_data["username"])
        DBSession().add(new_user)
        DBSession().commit()
        self.write({})


class ContactUsHandler(BaseHandler):

    def post(self):
        contact_data = json.loads(self.request.body)
        if not self.validate_input(["name","email", "body"], contact_data):
            return

        self.logit("Someone just used the 'Contact Us' form. )

        email_body = "Name: " + contact_data["name"] + "\n"
        email_body += "Email: " + contact_data["email"] + "\n"
        email_body += "Message: " + contact_data["body"] + "\n"
        self.send_email( settings["abuse_email"], "XSSHunter Contact Form Submission", email_body, "", "text" )

        self.write({
            "success": True,
        })


class HealthHandler(BaseHandler):

    def get(self):
        self.write("XSSHUNTER_OK")


class LogoutHandler(BaseHandler):

    def get(self):
        self.logit("User is logging out.")
        self.clear_cookie("user")
        self.clear_cookie("csrf")
        self.write({})
