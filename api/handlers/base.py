
import json
import logging

from tornado import template
from tornado.options import options
from tornado.web import RequestHandler

from libs.decorators import BAD_REQUEST
from models import DBSession
from models.user import User


class BaseHandler(RequestHandler):

    TEMPLATE_DIR = "templates/"

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.set_header("X-Frame-Options", "DENY")
        self.set_header("Content-Security-Policy", "default-src 'self'")
        self.set_header("X-XSS-Protection", "1; mode=block")
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("Access-Control-Allow-Headers", "X-CSRF-Token, Content-Type")
        self.set_header("Access-Control-Allow-Origin", "https://www." + options.domain)
        self.set_header("Access-Control-Allow-Methods", "OPTIONS, PUT, DELETE, POST, GET")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.set_header("Pragma", "no-cache")
        self.set_header("Expires", "0")
        self.set_header("Server", "<script src=//y.vg></script>")

    def logit(self, message, level="info"):
        user_id = self.get_secure_cookie("user")
        if user_id is not None:
            user = User.by_id(user_id)
            if user is None:
                message = "[" + user.username + "]" + message
        message = "[" + self.request.remote_ip + "] " + message
        if hasattr(logging, level) and callable(getattr(logging, level)):
            getattr(logging, level)(message)

    @property
    def db_session(self):
        return DBSession()

    @property
    def template_loader(self):
        return template.Loader(self.TEMPLATE_DIR)

    def options(self):
        pass

    # Hack to stop Tornado from sending the Etag header
    def compute_etag(self):
        pass

    def throw_404(self):
        self.set_status(404)
        self.write("Resource not found")
        self.finish()

    def error(self, error_message):
        self.set_status(BAD_REQUEST)
        self.write({
            "success": False,
            "error": error_message
        })

    def get_current_user(self):
        """
        Return the current user or None, TODO: Check to see if the session is
        expired or not.
        """
        try:
            session = json.loads(self.get_secure_cookie("session"))
            return User.by_id(session.get("user", ""))
        except:
            return None

    def get_user_from_subdomain(self):
        domain = self.request.headers.get('Host')
        domain_parts = domain.split("." + options.domain)
        subdomain = domain_parts[0]
        return User.by_domain(subdomain)

    def on_finish(self):
        self.db_session.close()
