"""
Combines the .js files for us
"""

import os
import json

from cStringIO import StringIO


class Probe(object):

    # The order here is important!
    JS_FILES = [
        "header.js",
        "html2canvas.js",
        "openpgp.js",
        "probe.js"
    ]
    PGP_TEMPLATE = "pgp_encrypted_template.txt"
    _js_cache = None
    _pgp_cache = None

    @classmethod
    def path_for(cls, filename):
        _probejs_dir = os.path.join(os.getcwd(), "probe", "js")
        filepath = os.path.join(_probejs_dir, filename)
        assert os.path.exists(filepath) and os.path.isfile(filepath)
        return filepath

    @classmethod
    def load_js(cls, no_cache=False):
        """ Concats all of the .js files together in the specified order """
        if cls._js_cache is None or no_cache:
            probe = StringIO()
            for filename in cls.JS_FILES:
                with open(cls.path_for(filename), "rb") as fp:
                    probe.write(fp.read())
            cls._js_cache = probe.getvalue()
        return cls._js_cache

    @classmethod
    def load_pgp(cls, no_cache=False):
        if cls._pgp_cache is None or no_cache:
            with open(cls.path_for(cls.PGP_TEMPLATE), "rb") as template:
                cls._pgp_cache = json.dumps(template.read())
        return cls._pgp_cache

    @classmethod
    def js(cls, _id, domain, pgp_key, chainload, collections, no_cache=False):
        """
        Constructs a personalized payload, this is an extremely ineffiecent
        method but whatever we got plenty of memory (hopefully). Maybe we'll
        come back and optimize it later.
        """
        js = cls.load_js(no_cache)
        js = js.replace('[HOST_URL]', "https://" + domain) \
            .replace('[PGP_REPLACE_ME]', json.dumps(pgp_key)) \
            .replace('[CHAINLOAD_REPLACE_ME]', json.dumps(chainload)) \
            .replace('[COLLECT_PAGE_LIST_REPLACE_ME]', json.dumps(collections))
        if len(pgp_key):
            js = js.replace('[TEMPLATE_REPLACE_ME]', cls.load_pgp(no_cache))
        else:
            js = js.replace('[TEMPLATE_REPLACE_ME]', "''")
        return js.replace("[PROBE_ID]", _id)
