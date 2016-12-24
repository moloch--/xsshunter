# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

import functools
import json
import logging

from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from tornado.options import options

# Session expires in `x` seconds
SESSION_EXPIRES = 3600  # 1 hr

# HTTP 400
BAD_REQUEST = 400
SERVER_ERROR = 500
FORBIDDEN = 403  # Authentication
NOT_AUTHENTICATED = 403
NOT_AUTHORIZED = 418  # Authorization
NOT_FOUND = 404
JSON_SCHEMA_ERROR = "json-schema-error"


def json_api(schema):
    """
    This is a simple wrapper to make JSON API more consistent. If the wrapped
    method raises an exception, this will return a JSON error message. It can
    also optionally validate a request schema if one is provided (else None).
    """

    def func(method):
        @functools.wraps(method)
        def wrapper(self, *method_args, **method_kwargs):
            logging.debug("JSON Schema for %s -> %s", self.request.method,
                          self.__class__)
            try:
                json_req = json.loads(self.request.body)
                if schema is not None:
                    logging.debug("Validating json schema")
                    validate(json_req, schema)
                elif self.request.method not in ["GET", "HEAD", "DELETE"]:
                    raise SchemaError("Request method %s must have a schema" %
                                      self.request.method)
                else:
                    logging.debug("No json schema for request, skipping")

                return method(self, json_req, *method_args, **method_kwargs)
            except (ValidationError, ValidationError) as error:
                self.set_status(BAD_REQUEST)
                self.write({
                    "error": str(error)
                })
                self.finish()
            except SchemaError as error:
                self.set_status(BAD_REQUEST)
                if options.debug:
                    logging.exception("Request triggered exception")
                    self.write({
                        "error": str(error)
                    })
                else:
                    self.write({
                        "error": "JSON request not formatted properly"
                    })
                self.finish()
        return wrapper
    return func


def authenticated(method):
    """ Checks to see if a user has been authenticated """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        if user is not None and not user.locked:
            return method(self, *args, **kwargs)
        else:
            logging.debug("User from session does not exist")
        self.set_status(NOT_AUTHENTICATED)
        self.write({
            "error": "You are not authenticated"
        })
    return wrapper


def authorized(permission):
    """ Checks user's permissions """

    def func(method):

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            user = self.get_current_user()
            if user is not None and user.has_permission(permission):
                return method(self, *args, **kwargs)
            else:
                logging.warning("Rejecting unauthorized request from '%s'",
                                user.username)
            self.set_status(NOT_AUTHORIZED)
            self.write({"errors": "You are not authorized"})
        return wrapper

    return func
