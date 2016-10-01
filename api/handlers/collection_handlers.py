
from handlers.base import BaseHandler


class CollectPageHandler(BaseHandler):

    def initialize(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, HEAD, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'X-Requested-With')

    def post(self):
        user = self.get_user_from_subdomain()
        request_dict = json.loads(self.request.body)
        if not self.validate_input(["page_html", "uri"], request_dict):
            return

        if user is None:
            self.throw_404()
            return

        page = CollectedPage()
        page.uri = request_dict.get( "uri" )
        page.page_html = request_dict.get( "page_html" )
        page.owner_id = user.id
        page.timestamp = int(time.time())

        self.logit( "Received a collected page for user " + user.username + " with a URI of " + page.uri )

        session.add( page )
        session.commit()


class CollectedPagesHandler(BaseHandler):

    """
    Endpoint for querying for collected pages.

    By default returns past 25 payload fires

    Params:
        offset
        limit
    """

    def get(self):
        user = self.get_authenticated_user()
        offset = abs( int( self.get_argument('offset', default=0 ) ) )
        limit = abs( int( self.get_argument('limit', default=25 ) ) )
        results = session.query( CollectedPage ).filter_by( owner_id = user.id ).order_by( CollectedPage.timestamp.desc() ).limit( limit ).offset( offset )
        total = session.query( CollectedPage ).filter_by( owner_id = user.id ).count()

        self.logit( "User is retrieving collected pages.")

        return_list = []

        for result in results:
            return_list.append( result.to_dict() )

        return_dict = {
            "results": return_list,
            "total": total,
            "success": True
        }
        self.write( json.dumps( return_dict ) )

    def delete(self):
        delete_data = json.loads(self.request.body)

        if not self.validate_input( ["id"], delete_data ):
            return

        collected_page_db_record = session.query( CollectedPage ).filter_by( id=str( delete_data.get( "id" ) ) ).first()
        user = self.get_authenticated_user()

        if collected_page_db_record.owner_id != user.id:
            self.logit( "Just tried to delete a collected page that wasn't theirs! (ID:" + delete_data["id"] + ")", "warn")
            self.error( "Fuck off <3" )
            return

        self.logit( "User is deleting collected page with the URI of " + collected_page_db_record.uri )
        collected_page_db_record = session.query( CollectedPage ).filter_by( id=str( delete_data.get( "id" ) ) ).delete()
        session.commit()

        self.write({
            "success": True,
            "message": "Collected page deleted!",
        })
