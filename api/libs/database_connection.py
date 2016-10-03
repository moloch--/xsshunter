# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2015
"""

import logging

from furl import furl

PYTHON_POSTGRES_DRIVER = "psycopg2"


class DatabaseConnection(object):

    MAX_CONNECTION_ERRORS = 10

    def __init__(self, database, hostname='', port='',
                 username='', password='', dialect=''):
        """
        Takes all the arguments and constructs the connection string based on
        the SQL dialect.
        """
        self._connection_url = furl()
        self._connection_url.host = hostname
        self._connection_url.port = port
        self._connection_url.username = username
        self._connection_url.password = password
        sql_dialects = {
            'sqlite': self._sqlite,
            'sqlite3': self._sqlite,
            'postgres': self._postgresql,
            'postgresql': self._postgresql,
            'mysql': self._mysql
        }
        sql_dialects.get(dialect, self._postgresql)(database)

    def __str__(self):
        """ Construct the database connection string """
        return str(self._connection_url)

    def _postgresql(self, database):
        """ PostgreSQL specific URL construction """
        logging.debug("Configured to use PostgreSQL for a database")
        self._connection_url.path = database
        self._connection_url.scheme = "postgresql+%s" % PYTHON_POSTGRES_DRIVER

    def _sqlite(self, database):
        """ SQLite specific URL construction """
        self._connection_url.host = database
        self._connection_url.port = None
        self._connection_url.username = None
        self._connection_url.password = None
        self._connection_url.path = None
        self._connection_url.scheme = "sqlite"

    def _mysql(self, database):
        """ MySQL specific URL construction """
        logging.debug("Configured to use MySQL for a database")
        self._connection_url.path = database
        self._connection_url.scheme = "mysql"
