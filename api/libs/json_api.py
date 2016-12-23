# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2016
"""


import functools
import logging
import json

from tornado.options import options
from jsonschema import validate
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError as JsonValidationError
from libs.validation_errors import ValidationError
from sqlalchemy.exc import StatementError


# Session expires in `x` seconds
SESSION_EXPIRES = 3600  # 1 hr

# HTTP 400
JSON_SCHEMA_ERROR = "json-schema-error"
BAD_REQUEST = 400
SERVER_ERROR = 500
FORBIDDEN = 403  # Authentication
NOT_AUTHENTICATED = 403
NOT_AUTHORIZED = 418  # Authorization
NOT_FOUND = 404

PRIMARY_ID = {
    "type": "string",
    "minLength": 22,
    "maxLength": 25
}

PRIMARY_ID_LIST = {
    "type": "array",
    "items": {
        "type": "string",
        "minLength": 22,
        "maxLength": 25,
        "uniqueItems": True
    }
}


def json_api_method(schema):
    """
    This is a simple wrapper to make JSON API more consistent. If the wrapped
    method raises an exception, this will return a JSON error message. It can
    also optionally validation a request schema if one is provided (else None).
    """

    def func(method):
        @functools.wraps(method)
        def wrapper(self, *method_args, **method_kwargs):
            try:
                if schema is not None:
                    schema["additionalProperties"] = False
                    validate(self.api_request, schema)
                elif self.request.method not in ["GET", "HEAD", "DELETE"]:
                    raise SchemaError("Request method %s must have a schema" % self.request.method)
                return method(self, *method_args, **method_kwargs)
            except (JsonValidationError, ValidationError) as error:
                self.set_status(BAD_REQUEST)
                self.write({
                    "error": str(error)
                })
                self.finish()
            except SchemaError as error:
                self.set_status(BAD_REQUEST)
                if options.debug:
                    logging.exception('Request triggered exception')
                    self.write({
                        "error": "JSON schema: " + str(error)
                    })
                else:
                    self.write({
                        "error": "JSON request not formatted properly"
                    })
                self.finish()
            except StatementError:
                self.set_status(BAD_REQUEST)
                logging.exception('Request triggered exception')
                self.write({
                    "error": "JSON request not formatted properly"
                })
                self.finish()
        return wrapper
    return func
