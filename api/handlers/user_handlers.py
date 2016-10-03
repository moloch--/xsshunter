
from handlers.base import BaseHandler
from models import DBSession
from models.user import User
from probe import Probe

from libs.decorators import json_api, authenticated


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
        js = Probe.js(probe_id,
                      domain=user.domain,
                      gpg_key=user.pgp_key,
                      chainload=user.chainload_uri,
                      page_collections=user.page_collection_paths_list)
        self.set_header("Content-Type", "application/javascript")
        self.write(js)


class UserInformationHandler(BaseHandler):

    @authenticated
    def get(self):
        user = self.get_current_user()
        self.write(user.to_dict())

    @authenticated
    @json_api({
        "type": "object",
        "properties": {
            "gpg_key": {"type": "string"}
        }
    })
    def put(self):
        user = self.get_current_user()

        DBSession().add(user)
        DBSession().commit()
        self.write(user.to_dict())
