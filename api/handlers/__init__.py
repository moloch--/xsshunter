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

from handlers.public_handlers import LoginHandler
from handlers.public_handlers import RegisterHandler
from handlers.public_handlers import ContactUsHandler
from handlers.public_handlers import HealthHandler

from handlers.user_handlers import HomepageHandler


API_V2 = "/api/v2"

API_HANDLERS = [

    # Public handlers
    (API_V2 + r"/register", RegisterHandler),
    (API_V2 + r"/login", LoginHandler),
    (API_V2 + r"/contact", ContactUsHandler),
    (API_V2 + r"/health", HealthHandler),

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
