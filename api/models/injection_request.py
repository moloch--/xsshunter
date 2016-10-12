# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

from sqlalchemy import Column
from sqlalchemy.types import String, Text

from models import DatabaseObject


class InjectionRequest(DatabaseObject):

    request = Column(Text())
    injection_key = Column(String(100))
    owner_correlation_key = Column(String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "created": str(self.created),
            "request": self.request,
            "injection_key": self.injection_key
        }

    def __str__(self):
        return self.id
