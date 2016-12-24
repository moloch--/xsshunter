# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

from tornado.web import Application
from tornado.web import StaticFileHandler
from tornado.options import options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from handlers import public_handlers


API_V2 = "/api/v2"

API_HANDLERS = [

    # Public handlers
    (API_V2 + r"/registration", public_handlers.RegistrationHandler),
    (API_V2 + r"/login", public_handlers.LoginHandler),
    (API_V2 + r"/contact", public_handlers.ContactUsHandler),
    (API_V2 + r"/health", public_handlers.HealthHandler),

]


def start_api_server():
    """ Main entry point for the application """
    api_app = Application(
        handlers=API_HANDLERS,
        cookie_secret=options.cookie_secret,
        debug=options.debug)
    app_server = HTTPServer(api_app, xheaders=options.x_headers)
    app_server.listen(options.listen_port)
    try:
        io_loop = IOLoop.instance()
        io_loop.start()
    except KeyboardInterrupt:
        pass
    finally:
        io_loop.stop()
