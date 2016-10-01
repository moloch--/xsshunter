
import os
import gzip
import urllib
import json

from tornado.options import options
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class SendEmailMixin(object):

    """ Handles sending email """

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


class DatastoreMixin(object):

    """ Handles persistently storing data """

    DATASTORES = ["s3", "filesystem"]

    def save_data(self, filepath, data, datastore="filesystem"):
        datastore = "_%s_save" % datastore
        if datastore in self.CARRIERS and hasattr(self, datastore):
            assert callable(getattr(self, datastore))
            getattr(self, datastore)(filepath, data)

    def read_data(self, filepath, datastore="filesystem"):
        datastore = "_%s_read" % datastore
        if datastore in self.CARRIERS and hasattr(self, datastore):
            assert callable(getattr(self, datastore))
            return getattr(self, datastore)(filepath)

    def _filesystem_save(self, filepath, data):
        save_dir = os.path.join(os.getcwd(), options.datastore_filesystem_dir)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        filename = "_".join(filepath.split(os.sep))
        save_file = os.path.join(save_dir, filename)
        with gzip.open(save_file, mode="wb") as fp:
            fp.write(data)

    def _filesystem_read(self, filepath):
        save_dir = os.path.join(os.getcwd(), options.datastore_filesystem_dir)
        filename = "_".join(filepath.split(os.sep))
        save_file = os.path.join(save_dir, filename)
        if os.path.exists(save_file) and os.path.isfile(save_file):
            with gzip.open(save_file, mode="rb") as fp:
                return fp.read()
        else:
            raise ValueError("File not found")

    def _s3_save(self, filename, data):
        pass

    def _s3_read(self, filename, data):
        pass
