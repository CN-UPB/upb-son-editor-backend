from son.editor.users.usermanagement import get_user
from flask import session
from son.editor.app.database import db_session
from son.editor.models.workspace import Workspace


def check_access(request):
    group_index = request.url_rule._regex.groupindex
    if 'wsID' in group_index:
        wsid = group_index['wsID']
        if wsid:
            data_session = db_session()
            ws = data_session.query(Workspace).filter_by(id=wsid).first()
            if 'userData' in session:
                user = get_user(session['userData'])
                if user:
                    if ws in user.workspaces:
                        return True
            return False
        else:
            return True
    else:
        return True
