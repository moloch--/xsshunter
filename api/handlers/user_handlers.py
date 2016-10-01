
import json

from handlers.base import BaseHandler
from models import DBSession
from models.user import User
from probe import Probe


class HomepageHandler(BaseHandler):

    def initialize(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "OPTIONS, PUT, DELETE, POST, GET")
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type, Origin, Authorization, Accept, Accept-Encoding")

    def get(self, path):
        domain = self.request.headers.get('Host')
        user = User.by_domain(domain)

        if user is not None:
            self.send_probe(user)
        else:
            self.throw_404()

    def send_probe(self, user):
        probe_id = ""
        if self.request.uri != "/":
            probe_id = self.request.uri.split("/")[1]
        # Render a personalized probe.js
        js = Probe.js(probe_id, user.domain, user.pgp_key,
                      user.chainload_uri, user.page_collection_paths_list)
        self.set_header("Content-Type", "application/javascript")
        self.write(js)


class UserInformationHandler(BaseHandler):

    def get(self):
        user = self.get_authenticated_user()
        self.logit("User grabbed their profile information")
        if user is None:
            return
        self.write(user.get_user_blob())

    def put(self):
        user = self.get_authenticated_user()
        if user is None:
            return

        user_data = json.loads(self.request.body)

        # Mass assignment is dangerous mmk
        allowed_attributes = [
            "pgp_key", "full_name", "email", "password",
            "email_enabled", "chainload_uri", "page_collection_paths_list"
        ]
        invalid_attribute_list = []
        for key, value in user_data.iteritems():
            if key in allowed_attributes:
                return_data = user.set_attribute(key, user_data.get(key))
                if return_data is not True:
                    invalid_attribute_list.append(key)

        DBSession().commit()

        return_data = user.get_user_blob()

        if invalid_attribute_list:
            return_data["success"] = False
            return_data["invalid_fields"] = invalid_attribute_list
        else:
            self.logit("User just updated their profile information.")
            return_data["success"] = True

        self.write(return_data)
