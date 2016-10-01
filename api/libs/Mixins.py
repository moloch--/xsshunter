
import urllib
import json

from tornado.options import options
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class SendEmailMixin(object):

    CARRIERS = ["_mailgun"]

    def send_email(self, mail_to, subject, body, carrier="mailgun"):
        carrier = "_%s" % carrier
        if carrier in self.CARRIERS and hasattr(self, carrier):
            assert callable(getattr(self, carrier))
            getattr(self, carrier)(mail_to, subject, body)

    @property
    def _mailgun_api(self):
        return "https://api.mailgun.net/v3/%s/messages" % (
            options.mailgun_sending_domain)

    @coroutine
    def _mailgun(self, mail_to, subject, body):
        http_client = AsyncHTTPClient()
        email_data = {
            "from": urllib.quote_plus(options.mail_from),
            "to": urllib.quote_plus(mail_to),
            "subject": urllib.quote_plus(subject),
            "html": urllib.quote_plus(body),
        }
        request = HTTPRequest(self._mailgun_api,
                              method="POST",
                              headers={"Accept": "application/json"},
                              body=email_data,
                              validate_cert=True,
                              request_timeout=3.0)
        response = yield http_client.fetch(request)
        raise Return(json.loads(response.body)['response'])
