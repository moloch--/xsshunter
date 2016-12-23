# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

from handlers.base import BaseHandler

from libs.decorators import json_api, authenticated


class HomepageHandler(BaseHandler):

    @authenticated
    def get(self):
        user = self.get_current_user()
        self.write(user.to_dict())


class OtpHandler(BaseHandler):

    @authenticated
    @json_api({
        "type": "object",
        "properties": {
            "otp_enabled": {"type": "boolean"}
        }
    })
    def post(self):
        user = self.get_current_user()
        user.otp_enabled = bool(self.get_argument("otp_enabled", True))
        self.dbsession.add(user)
        self.dbsession.commit()
        if user.otp_enabled:
            self.write({
                "success": True,
                "provisioning_uri": user.otp_provisioning_uri
            })
        else:
            self.write({"success": True})


class PgpKeyHandler(BaseHandler):

    @authenticated
    @json_api({
        "type": "object",
        "properties": {
            "pgp_key": {"type": "string"}
        },
        "required": ["pgp_key"]
    })
    def post(self):
        user = self.get_current_user()
        user.pgp_key = self.get_argument("pgp_key", "")
        self.dbsession.add(user)
        self.dbsession.commit()
        self.write(user.to_dict())


class ApiKeyHandler(BaseHandler):

    @authenticated
    @json_api({
        "type": "object",
        "properites": {
            "api_key": {"type": "string"}
        }
    })
    def post(self):
        user = self.get_current_user()
        api_key = user.generate_api_key()
        self.dbsession.add(user)
        self.dbsession.commit()
        self.write({
            "success": True,
            "api_key": api_key
        })
