from son.editor.users.usermanagement import get_user
from flask import session
from son.editor.app.database import db_session
from son.editor.models.workspace import Workspace


# This method checks if the current user is allowed to access a given workspace
def check_access(request):
    # Access parsed values of the url
    group_index = request.url_rule._regex.groupindex

    # Check if wsID was in the url
    if 'wsID' in group_index:
        wsid = group_index['wsID']
        if wsid:
            data_session = db_session()
            ws = data_session.query(Workspace).filter_by(id=wsid).first()
            if 'userData' in session:
                # Get current user
                user = get_user(session['userData'])
                if user:
                    # If the requested workspace is in his workspaces, he is allowed to access it
                    if ws in user.workspaces:
                        return True
            return False
        else:
            # Should never be the case, but allow access if wsid is missing
            return True
    else:
        # He is allowed to access all other directories if no workspace is specified
        return True
