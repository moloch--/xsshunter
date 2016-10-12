# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016

Administrative controls
"""

from base import BaseHandler
from models.user import User
from models.permission import ADMIN_PERMISSION
from decorators import authenticated, authorized, json_api


class UserManagementHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self):
        pass

    @authenticated
    @authorized(ADMIN_PERMISSION)
    @json_api({
        "type": "object",
        "properties": {
            "user_id": {"type", "string"},
            "locked": {"type": "boolean"}
        }
    })
    def post(self, req):
        user = User.by_id(req.get("user_id", ""))
        user.locked = bool(req.get("locked", True))
        self.db_session.add(user)
        self.db_session.commit()
        self.write({
            "success": True,
            "user": user.to_admin_dict()
        })


class GodModeHandler(BaseHandler):

    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self):
        pass
