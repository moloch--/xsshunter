
from tornado.web import Application
from tornado.web import StaticFileHandler
from tornado.options import options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from handlers.public_handlers import LoginHandler
from handlers.public_handlers import LogoutHandler
from handlers.public_handlers import RegisterHandler
from handlers.public_handlers import ContactUsHandler
from handlers.public_handlers import HealthHandler

from handlers.user_handlers import HomepageHandler
from handlers.user_handlers import UserInformationHandler

from handlers.collection_handlers import CollectPageHandler
from handlers.collection_handlers import CollectedPagesHandler

from handlers.injection_handlers import InjectionHandler
from handlers.injection_handlers import InjectionRequestHandler
from handlers.injection_handlers import ResendInjectionEmailHandler

from handlers.xss_handlers import XSSPayloadFiresHandler
from handlers.xss_handlers import CallbackHandler


API_HANDLERS = [

    # Public handlers
    (r"/api/register", RegisterHandler),
    (r"/api/login", LoginHandler),
    (r"/api/logout", LogoutHandler),
    (r"/api/contactus", ContactUsHandler),
    (r"/health", HealthHandler),

    # Collection handlers
    (r"/api/collected_pages", CollectedPagesHandler),
    (r"/page_callback", CollectPageHandler),

    # Injection handlers
    (r"/api/injection", InjectionHandler),
    (r"/api/record_injection", InjectionRequestHandler),
    (r"/api/resend_injection_email", ResendInjectionEmailHandler),

    # XSS handlers
    (r"/api/payloadfires", XSSPayloadFiresHandler),
    (r"/js_callback", CallbackHandler),

    # Static file handlers
    (r"/uploads/(.*)", StaticFileHandler, {"path": "uploads/"}),

    # User handlers
    (r"/api/user", UserInformationHandler),
    (r"/(.*)", HomepageHandler),

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
