# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2015
"""

import time
import logging

from tornado.options import options
from sqlalchemy import event, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from libs.ConsoleColors import R, W, BLU, BOLD
from libs.DatabaseConnection import DatabaseConnection


if options.db_debug:

    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)

    # This benchmarks the amount of time spent quering the database
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context,
                              executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context,
                             executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        color = R if total > 0.01 else BLU
        logging.debug("Total query time: %s%s%f%s", BOLD, color, total, W)


db_connection = DatabaseConnection(database=options.sql_database,
                                   hostname=options.sql_host,
                                   port=options.sql_port,
                                   username=options.sql_user,
                                   password=options.sql_password,
                                   dialect=options.sql_dialect)


# Setup the database session
engine = create_engine(str(db_connection),
                       pool_recycle=options.sql_pool_recycle)
setattr(engine, 'echo', options.db_debug)
#  _Session = sessionmaker(bind=engine)

# Main export
DBSession = scoped_session(sessionmaker(autoflush=True,
                                        autocommit=False,
                                        bind=engine))
