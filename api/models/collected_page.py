# -*- coding: utf-8 -*-
"""
@author: moloch, mandatory
Copyright 2015
"""

from sqlalchemy import Column
from sqlalchemy.types import String, Text

from models.base import DatabaseObject


class CollectedPage(DatabaseObject):

    uri = Column(Text())
    page_html = Column(Text())
    owner_id = Column(String(100))

    def to_dict(self):
        return {
            "uri": self.uri,
            "id": self.id,
            "page_html": self.page_html,
            "timestamp": str(self.created)
        }

    def __str__(self):
        return self.id
