# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

from sqlalchemy import Column, ForeignKey, and_
from sqlalchemy.types import Unicode

from libs.sql_datatypes import UUIDType
from models import DBSession
from models.base import DatabaseObject

# Permission constants
ADMIN_PERMISSION = u'admin'


class Permission(DatabaseObject):

    """ Permission definition """

    NAME_LENGTH = 64
    name = Column(Unicode(NAME_LENGTH), nullable=False)
    user_id = Column(UUIDType(), ForeignKey('user._id'), nullable=False)

    @classmethod
    def by_user_and_name(cls, user, name):
        """ Get a permission object based on name and user """
        return DBSession().query(cls).filter(and_(
            cls.name == unicode(name[:cls.NAME_LENGTH]),
            cls.user_id == user.id
        )).first()

    def __repr__(self):
        return '<Permission - name: %s, user_id: %d>' % (
            self.name, self.user_id)

    def __unicode__(self):
        return self.name
