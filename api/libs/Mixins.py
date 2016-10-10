
import gzip
import json
import os
import urllib

from hashlib import sha256
from tornado.gen import Return, coroutine
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.options import options


class SendEmailMixin(object):

    """ Handles sending email """

    CARRIERS = ["mailgun"]

    def send_email(self, mail_to, subject, body, carrier="mailgun"):
        assert carrier in self.CARRIERS
        carrier = "_%s" % carrier
        if hasattr(self, carrier) and callable(getattr(self, carrier)):
            getattr(self, carrier)(mail_to, subject, body)
        else:
            raise ValueError("Carrier does not support %s" % carrier)

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


class PersistentDataMixin(object):

    """
    Handles persistently storing data, it's a basic key/value storage bucket.

    Filesystem: Files are stored GZip'd in the SHA256 of the `filepath`
                this datastore also requires a writable filesystem (duh)
    """

    DATASTORES = ["s3", "filesystem"]

    def save_data(self, filepath, data, datastore="filesystem"):
        assert datastore in self.DATASTORES
        datastore = "_%s_save" % datastore
        if datastore in self.CARRIERS and hasattr(self, datastore):
            assert callable(getattr(self, datastore))
            getattr(self, datastore)(filepath, data)
        else:
            raise ValueError("Datastore does not support %s" % (datastore))

    def read_data(self, filepath, datastore="filesystem"):
        assert datastore in self.DATASTORES
        datastore = "_%s_read" % datastore
        if datastore in self.CARRIERS and hasattr(self, datastore):
            assert callable(getattr(self, datastore))
            return getattr(self, datastore)(filepath)
        else:
            raise ValueError("Datastore does not support %s" % (datastore))

    def delete_data(self, filepath, datastore="filesystem"):
        assert datastore in self.DATASTORES
        datastore = "_%s_delete" % datastore
        if datastore in self.CARRIERS and hasattr(self, datastore):
            assert callable(getattr(self, datastore))
            return getattr(self, datastore)(filepath)
        else:
            raise ValueError("Datastore does not support %s" % (datastore))

    def _filesystem_save(self, filepath, data):
        """
        It is the caller's responsibility to track filenames/access/etc, we're
        just a blind key<->value data store.
        """
        save_dir = os.path.join(os.getcwd(), options.datastore_filesystem_dir)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        filename = sha256(filepath).hexdigest()
        save_file = os.path.join(save_dir, filename)
        if os.path.exists(save_file):
            raise ValueError("File already exists")
        with gzip.open(save_file, mode="wb") as fp:
            fp.write(data)

    def _filesystem_read(self, filepath):
        save_dir = os.path.join(os.getcwd(), options.datastore_filesystem_dir)
        filename = sha256(filepath).hexdigest()
        save_file = os.path.join(save_dir, filename)
        if os.path.exists(save_file) and os.path.isfile(save_file):
            with gzip.open(save_file, mode="rb") as fp:
                return fp.read()
        else:
            raise ValueError("File not found")

    def _filesystem_delete(self, filepath):
        save_dir = os.path.join(os.getcwd(), options.datastore_filesystem_dir)
        filename = sha256(filepath).hexdigest()
        save_file = os.path.join(save_dir, filename)
        if os.path.exists(save_file) and os.path.isfile(save_file):
            os.unlink(save_file)
        else:
            raise ValueError("File not found")

    def _s3_save(self, filename, data):
        pass

    def _s3_read(self, filename, data):
        pass

    def _s3_delete(self, filename, data):
        pass
