"""
Combines the .js files for us
"""

import os

from cStringIO import StringIO


class Probe(object):

    # The order here is important!
    FILES = [
        "header.js",
        "html2canvas.js",
        "openpgp.js",
        "probe.js"
    ]
    _cache = None

    @classmethod
    def path_for(cls, filename):
        _probejs_dir = os.path.join(os.getcwd(), "probe", "js")
        filepath = os.path.join(_probejs_dir, filename)
        assert os.path.exists(filepath) and os.path.isfile(filepath)
        return filepath

    @classmethod
    def js(cls, no_cache=False):
        """ Concats all of the .js files together in the specified order """
        if cls._cache is None or no_cache:
            probe = StringIO()
            for filename in cls.FILES:
                with open(cls.path_for(filename), "rb") as fp:
                    probe.write(fp.read())
            cls._cache = probe.getvalue()
        return cls._cache
