# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2016
"""
# pylint: disable=C0103


import re
import uuid
from base64 import urlsafe_b64encode
from datetime import datetime

from sqlalchemy import Column, event
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.types import DateTime

from libs.DatabaseDatatypes import UUIDType
from models import DBSession


class _DatabaseObject(object):

    """
    All database objects inherit from this object, it automatically
    creates a primary key, a `created` datetime and the sets the tablename
    by converting the classname to snake case.
    """

    _id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow)

    @declared_attr
    def __tablename__(self):
        """ Converts name from camel case to snake case """
        name = self.__name__
        return (
            name[0].lower() +
            re.sub(r'([A-Z])',
                   lambda letter: "_" + letter.group(0).lower(), name[1:]))

    @property
    def id(self):
        """ Return the urlsafe_b64encode version of the UUID primary key """
        if self._id is None:
            self._id = uuid.uuid4()  # Coercion occurs on commit()
            return urlsafe_b64encode(self._id.bytes)
        else:
            return self._id

    @classmethod
    def all(cls):
        """ Returns a list of all objects in the database """
        return DBSession().query(cls).all()

    @classmethod
    def by_id(cls, guid):
        """
        Returns a the object with id of guid, can accept a string of UUID class
        """
        return DBSession().query(cls).filter_by(_id=guid).first()



# Create a usable class with SQLAlchemy's declarative_base
DatabaseObject = declarative_base(cls=_DatabaseObject)

# Place a hook for `updated' attribute
# pylint: disable=W0613
@event.listens_for(DatabaseObject, "before_update", propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated = datetime.utcnow()
