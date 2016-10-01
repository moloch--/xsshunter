
import json

from handlers.base import BaseHandler
from models import DBSession


class HomepageHandler(BaseHandler):

    def initialize(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "OPTIONS, PUT, DELETE, POST, GET")
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type, Origin, Authorization, Accept, Accept-Encoding")

    def get(self, path):
        domain = self.request.headers.get('Host')
        user = self.get_user_from_subdomain()

        if user is None:
            self.throw_404()
            return

        with open("./probe.js") as fp:
            new_probe = fp.read()
        new_probe.replace('[HOST_URL]', "https://" + domain) \
            .replace('[PGP_REPLACE_ME]', json.dumps(user.pgp_key)) \
            .replace('[CHAINLOAD_REPLACE_ME]', json.dumps(user.chainload_uri)) \
            .replace('[COLLECT_PAGE_LIST_REPLACE_ME]', json.dumps(user.get_page_collection_path_list()))

        if len(user.pgp_key):
            with open("templates/pgp_encrypted_template.txt", "r") as template_handler:
                new_probe = new_probe.replace('[TEMPLATE_REPLACE_ME]', json.dumps(template_handler.read()))
        else:
            new_probe = new_probe.replace('[TEMPLATE_REPLACE_ME]', json.dumps(""))

        if self.request.uri != "/":
            probe_id = self.request.uri.split("/")[1]
            self.write(new_probe.replace("[PROBE_ID]", probe_id))
        else:
            self.write(new_probe)


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
        allowed_attributes = ["pgp_key", "full_name", "email", "password", "email_enabled", "chainload_uri", "page_collection_paths_list" ]
        invalid_attribute_list = []
        tmp_domain = user.domain
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
