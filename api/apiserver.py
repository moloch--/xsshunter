#!/usr/bin/env python

import os
import logging

from tornado.options import define, options

# API Settings
define("origin",
       group="application",
       default=os.environ.get('API_ORIGIN', "wss://localhost"),
       help="validate websocket connections against this origin")

define("listen_port",
       group="application",
       default=os.environ.get('API_LISTEN_PORT', "8888"),
       help="run instances starting the given port",
       type=str)

define("x_headers",
       group="application",
       default=True,  # This app should always be behind nginx
       help="honor the `X-FORWARDED-FOR` and `X-REAL-IP` http headers",
       type=bool)

# Database settings
define("sql_dialect",
       group="database",
       default=os.environ.get("API_SQL_DIALECT", "postgres"),
       help="define the type of database (mysql|postgres|sqlite)")

define("sql_database",
       group="database",
       default=os.environ.get("API_SQL_DATABASE", "app"),
       help="the sql database name")

define("sql_host",
       group="database",
       default=os.environ.get("API_SQL_HOST", "127.0.0.1"),
       help="database sever hostname")

define("sql_port",
       group="database",
       default="3306",
       help="database tcp port")

define("sql_user",
       group="database",
       default=os.environ.get("API_SQL_USER", "app"),
       help="database username")

define("sql_password",
       group="database",
       default=os.environ.get("API_SQL_PASSWORD", "badpassword"),
       help="database password, if applicable")

define("sql_pool_recycle",
       group="database",
       default=int(os.environ.get("API_SQL_POOL_RECYCLE", 3600)),
       help="timeout to refresh dbapi connections (seconds)",
       type=int)

# Cookie settings
define("cookie_secret",
       group="secret",
       default=os.environ.get("API_COOKIE_SECRET", os.urandom(32).encode('hex')),
       help="the cookie hmac secret",
       type=str)


def start_api():
    """ Starts the main application """
    from handlers import start_api_server
    if options.debug:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
    start_api_server()


def main():
    start_api()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    options.parse_command_line()
    main()
