# -*- coding: utf-8 -*-
"""
@author: moloch, mandatory
Copyright 2015
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Text

from libs.database_datatypes import UUIDType
from models.base import DatabaseObject


class CollectedPage(DatabaseObject):

    owner_id = Column(UUIDType(), ForeignKey('user._id'), nullable=False)
    uri = Column(Text())
    page_html = Column(Text())

    def to_dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "page_html": self.page_html,
            "created": str(self.created)
        }

    def __str__(self):
        return self.id
