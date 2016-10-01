"""
Combines the .js files for us
"""

import os
import json

from base64 import b64encode
from cStringIO import StringIO
from collections import OrderedDict


class Probe(object):

    # The order here is important!
    RENDER_VARS = "--- RENDER_VARIABLES ---"
    JS_FILES = OrderedDict([
        ("header.js", ""),
        ("html2canvas.js", ""),
        ("openpgp.js", ""),
        (RENDER_VARS, None),
        ("probe.js", "")
    ])
    PGP_TEMPLATE = "pgp_encrypted_template.txt"
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
            for filename in cls.JS_FILES:
                with open(cls.path_for(filename), "rb") as fp:
                    cls.JS_FILES[filename] = fp.read()

    @classmethod
    def load_pgp(cls, no_cache=False):
        if cls._pgp_cache is None or no_cache:
            with open(cls.path_for(cls.PGP_TEMPLATE), "rb") as template:
                cls._pgp_cache = json.dumps(template.read())
        return cls._pgp_cache

    @classmethod
    def js(cls, no_cache=False, **kwargs):
        """
        Constructs a personalized payload, kwargs will be written into the file
        as JavaScript strings. Currently strings are the only supported JS
        data type.
        """
        cls.load_js(no_cache)
        probe = StringIO()
        for filename in cls.JS_FILES:
            if filename == cls.RENDER_VARS:
                probe.write("\n// --- Start Render Variables ---\n")
                for var, value in kwargs:
                    probe.write('var %s = atob("%s");\n' % (
                        var, b64encode(value)
                    ))
                if len(kwargs.get("pgp_key", "")):
                    probe.write('var pgp_email_template = atob("%s");\n' % (
                        b64encode(cls.load_pgp(no_cache))
                    ))
                probe.write("\n// --- End Render Variables ---\n")
            else:
                probe.write(cls.JS_FILES[filename])
        return probe.getvalue()
