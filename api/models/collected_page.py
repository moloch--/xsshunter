# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Text

from libs.database_datatypes import UUIDType
from models import DBSession, and_
from models.base import DatabaseObject


class CollectedPage(DatabaseObject):

    owner_id = Column(UUIDType(), ForeignKey('user._id'), nullable=False)
    uri = Column(Text())
    page_html = Column(Text())

    @classmethod
    def by_owner_and_id(cls, owner, collected_page_id):
        return DBSession().query(cls).filter(and_(
            cls.owner_id == owner.id,
            cls._id == collected_page_id
        )).first()

    def to_dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "page_html": self.page_html,
            "created": str(self.created)
        }

    def __str__(self):
        return self.id
