# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2015
"""


import json
import logging
import time
import traceback

from urlparse import urlparse

from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.web import HTTPError, RequestHandler, decode_signed_value
from tornado.websocket import WebSocketHandler

from libs.decorators import authenticated
from libs.validation_errors import ValidationError
from models import DBSession
from models.user import User


SESSION_EXPIRES = 3600 * 6


class BaseHandler(RequestHandler):

    """ User handlers extend this class """

    io_loop = IOLoop.instance()
    config = options

    def initialize(self):
        """ Setup sessions, etc """
        self._session = None
        self._dbsession = None
        self._user = None

    @property
    def dbsession(self):
        if self._dbsession is None:
            self._dbsession = DBSession()
        return self._dbsession

    def get_current_user(self):
        """ Get current user object from database """
        if self.session is not None:
            try:
                if self._user is None:
                    self._user = User.by_id(self.session['user_id'])
                assert self._user is not None
                return self._user
            except KeyError:
                logging.exception("Malformed session: %r", self.session)
            except AssertionError:
                logging.error("Failed to find user in database with id %r",
                              self.session['user_id'])
            except:
                logging.exception("Failed call to get_current_user()")
        return None

    @property
    def session(self):
        """ Lazily get the session data """
        if self._session is None:
            self._session = self.get_session()
        return self._session

    def start_session_for(self, user):
        """ Starts a new session """
        session = {
            'user_id': user.id,
            'expires': int(time.time()) + SESSION_EXPIRES,
        }
        return session

    def get_session(self):
        """ Deserialze session object, check the timestamp too """
        try:
            data = self.request.headers.get('X-XSS-HUNTER', None)
            if data is not None:
                session = json.loads(decode_signed_value(
                    secret=self.application.settings["cookie_secret"],
                    name="session",
                    value=data))
                if int(time.time()) <= session['expires']:
                    return session
            else:
                logging.debug("Unauthenticated, no session data")
        except:
            logging.exception("Failed to deserialze session data")
        return None

    def set_default_headers(self):
        """ Set security HTTP headers """
        self.set_header("Server", "XSS-HUNTER")

    def write(self, response):
        """
        Overloaded to get around Tornado's anti-JSON Hijacking. We don't care
        about it because our GET requests require a custom HTTP header.
        """
        if isinstance(response, list):
            response = json.dumps(response)
        super(BaseHandler, self).write(response)

    def write_error(self, status_code, **kwargs):
        """ Write our custom error pages """
        if not options.debug:
            trace = "".join(traceback.format_exception(*kwargs["exc_info"]))
            logging.error("Request from %s resulted in an error code %d:\n%s",
                          self.request.remote_ip, status_code, trace)
            if status_code in [403]:
                self.write({'error': '403'})
            elif status_code in [500, 503]:
                self.write({'error': 'Invalid request will be ignored'})
        else:
            # If debug mode is enabled, just call Tornado's write_error()
            super(BaseHandler, self).write_error(status_code, **kwargs)

    @authenticated
    def get(self, *args, **kwargs):
        """ Placeholder, incase child class does not impl this method """
        pass

    @authenticated
    def post(self, *args, **kwargs):
        """ Placeholder, incase child class does not impl this method """
        pass

    @authenticated
    def put(self, *args, **kwargs):
        """ Log odd behavior, this should never get legitimately called """
        logging.warn("%s attempted to use PUT method", self.request.remote_ip)
        super(BaseHandler, self).put(*args, **kwargs)

    @authenticated
    def delete(self, *args, **kwargs):
        """ Log odd behavior, this should never get legitimately called """
        logging.warn("%s attempted to use DELETE method",
                     self.request.remote_ip)
        super(BaseHandler, self).delete(*args, **kwargs)

    @authenticated
    def head(self, *args, **kwargs):
        """ Ignore it """
        logging.warn("%s attempted to use HEAD method", self.request.remote_ip)
        super(BaseHandler, self).head(*args, **kwargs)

    @authenticated
    def options(self, *args, **kwargs):
        """ Log odd behavior, this should never get legitimately called """
        logging.warn("%s attempted to use OPTIONS method",
                     self.request.remote_ip)
        super(BaseHandler, self).options(*args, **kwargs)

    def check_xsrf_cookie(self):
        """
        This method is automatically called for POST requests, for our
        anti-CSRF we just make sure that the X-XSS-HUNTER header in is in the
        request, and it contains a string of non-zero length. This is a some
        what redundent check since @authenticated also checks this header on
        *any* authenticated request (even GETs) whereas this method only checks
        POST requests.
        """
        token = self.request.headers.get("X-XSS-HUNTER", None)
        if not token or len(token) < 1:
            raise HTTPError(403, "Missing X-XSS-HUNTER header in request")



class APIBaseHandler(BaseHandler):

    """
    This is a nice little wrapper to make it easier for classes to handle and
    respond to JSON requests.
    """

    # This is the upper limit of JSON we'll parse
    MAX_BODY_LENGTH = (1024 * 256) # 256Kb

    def initialize(self):
        self.set_header("Content-type", "application/json; charset=UTF-8")
        self._session = None
        self._dbsession = None
        self._user = None
        # This is our anti-json hijacking header, it should be in GETs too
        # it is also what carries the session data.
        if self.request.headers.get("X-XSS-HUNTER", None) is None:
            raise HTTPError(403, "Missing header X-XSS-HUNTER")
        try:
            if 0 < len(self.request.body):
                if len(self.request.body) < self.MAX_BODY_LENGTH:
                    self.api_request = json.loads(self.request.body)
                else:
                    self.api_request = None
                    logging.critical('JSON body of %d exceeds MAX_BODY_LENGTH of %d',
                                     len(self.request.body),
                                     self.MAX_BODY_LENGTH)
            else:
                self.api_request = None
        except:
            logging.exception("%sException while parsing request body: %r",
                              "\nURL: %r\n" % self.request.uri,
                              self.request.body)

    def get_argument(self, name, default=None):
        """
        Instead of pulling from the body or GET parameters, we pull from the
        JSON body of the request, and expose an identical API. If there was no
        request body, we just return `None', falling back to calling super()
        or pulling arguments from the URI could introduce security problems.
        """
        if self.api_request is not None:
            return self.api_request.get(name, default)

    def get_uri_argument(self, name, default=None):
        """ If we really need to pull normal arguments """
        return super(APIBaseHandler, self).get_argument(name, default)
