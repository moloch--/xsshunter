# -*- coding: utf-8 -*-
"""
@author: mandatory, moloch
Copyright 2016
"""

from libs.decorators import authenticated, json_api
from handlers.base import BaseHandler
from models.collected_page import CollectedPage


class CollectPageHandler(BaseHandler):

    def initialize(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, HEAD, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')

    @authenticated
    @json_api({
        "type": "object",
        "properties": {
        }
    })
    def post(self, req):
        user = self.get_user_from_subdomain()
        if user is None:
            self.throw_404()
            return
        page = CollectedPage()
        page.uri = req.get("uri", "")
        page.page_html = req.get("page_html", "")
        user.collected_pages.append(page)

        self.logit("Received a collected page for user " + user.username + " with a URI of " + page.uri)
        self.db_session.add(page)
        self.db_session.add(user)
        self.db_session.commit()


class CollectedPagesHandler(BaseHandler):

    """
    Endpoint for querying for collected pages.

    By default returns past 25 payload fires

    Params:
        offset
        limit
    """

    @authenticated
    def get(self):
        user = self.get_current_user()
        offset = abs(int(self.get_argument('offset', default=0)))
        limit = abs(int(self.get_argument('limit', default=25)))
        results = CollectedPage.by_owner(user, limit, offset)
        self.write({
            "results": [page.to_dict() for page in results],
            "total": len(user.collected_pages),
            "success": True
        })

    @authenticated
    @json_api({
        "type": "object",
        "properties": {
            "id": {"type": "string"}
        }
    })
    def delete(self, req):
        user = self.get_current_user()
        page_id = req.get("id", "")

        collected_page = CollectedPage.by_owner_and_id(user, page_id)

        self.logit("User is deleting collected page with the URI of %r" % (
            collected_page.uri
        ))
        self.db_session.delete(collected_page)
        self.db_session.commit()
        self.write({
            "success": True,
            "message": "Collected page deleted!",
        })
