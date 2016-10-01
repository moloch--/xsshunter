
import json
import logging

from tornado.web import RequestHandler

from models import DBSession
from models.user import User


class BaseHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)

        if self.request.uri.startswith( "/api/" ):
            self.set_header("Content-Type", "application/json")
        else:
            self.set_header("Content-Type", "application/javascript")

        self.set_header("X-Frame-Options", "deny")
        self.set_header("Content-Security-Policy", "default-src 'self'")
        self.set_header("X-XSS-Protection", "1; mode=block")
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("Access-Control-Allow-Headers", "X-CSRF-Token, Content-Type")
        self.set_header("Access-Control-Allow-Origin", "https://www." + settings["domain"])
        self.set_header("Access-Control-Allow-Methods", "OPTIONS, PUT, DELETE, POST, GET")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.set_header("Pragma", "no-cache")
        self.set_header("Expires", "0")
        self.set_header("Server", "<script src=//y.vg></script>")

        self.request.remote_ip = self.request.headers.get("X-Forwarded-For")

        if not self.validate_csrf_token() and self.request.uri not in CSRF_EXEMPT_ENDPOINTS and not self.request.uri.startswith( "/b" ):
            self.error("Invalid CSRF token provided!")
            self.logit("Someone did a request with an invalid CSRF token!", "warn")
            self.finish()

    def logit(self, message, message_type="info"):
        user_id = self.get_secure_cookie("user")
        if user_id is not None:
            user = User.by_id(user_id)
            if user is None:
                message = "[" + user.username + "]" + message

        message = "[" + self.request.remote_ip + "] " + message
        if hasattr(logging, message_type):
            getattr(logging, message_type)(message)

    def options(self):
        pass

    # Hack to stop Tornado from sending the Etag header
    def compute_etag(self):
        return None

    def throw_404(self):
        self.set_status(404)
        self.write("Resource not found")

    def on_finish(self):
        DBSession().close()

    def validate_csrf_token(self):
        csrf_token = self.get_secure_cookie("csrf")

        if csrf_token is None:
            return True

        if self.request.headers.get('X-CSRF-Token') == csrf_token:
            return True

        if self.get_argument('csrf', False) == csrf_token:
            return True

        return False

    def validate_input(self, required_field_list, input_dict):
        for field in required_field_list:
            if field not in input_dict:
                self.error("Missing required field '" + field + "', this endpoint requires the following parameters: " + ', '.join( required_field_list ) )
                return False
            if input_dict[field] == "":
                self.error( "Missing required field '" + field + "', this endpoint requires the following parameters: " + ', '.join( required_field_list ) )
                return False
        return True

    def error(self, error_message):
        self.write(json.dumps({
            "success": False,
            "error": error_message
        }))

    def get_authenticated_user(self):
        user_id = self.get_secure_cookie("user")
        if user_id is None:
            self.error("You must be authenticated to perform this action!")
        return User.by_id(user_id)

    def get_user_from_subdomain(self):
        domain = self.request.headers.get('Host')
        domain_parts = domain.split("." + settings["domain"])
        subdomain = domain_parts[0]
        return User.by_domain(subdomain)
