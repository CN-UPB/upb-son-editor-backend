from flask import session

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound, UnauthorizedException
from son_editor.impl.usermanagement import get_user
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.constants import PROJECTS


def check_access(request):
    """
    checks if the current user is allowed to access a given resource.
    Session will be invalidated if the login information cannot be found

    :param request: The http request made to the server
    :return: nothing if access granted
    :raises UnauthorizedException: if user not logged in
    """
    if not all(key in session for key in ['user_data', 'access_token']):
        session.clear()
        raise UnauthorizedException("Session invalid. Please try logging in again")

    # Access parsed values of the url
    # Check if wsID was in the url
    if request.view_args is None:
        return
    if 'ws_id' in request.view_args:
        ws_id = request.view_args['ws_id']
        data_session = db_session()
        ws = data_session.query(Workspace).filter_by(id=ws_id).first()
        # Get current user
        user = get_user(session['user_data']['login'])
        # If the requested workspace is in his workspaces, he is allowed to access it
        if ws in user.workspaces:
            if 'project_id' in request.view_args:
                pj_id = request.view_args['project_id']
                pj = data_session.query(Project).filter(Project.id == pj_id).first()
                if pj in ws.projects:
                    return
                else:
                    raise NotFound("Project not found")
            elif 'parent_id' in request.view_args and PROJECTS in request.url.split("/"):
                pj_id = request.view_args['parent_id']
                pj = data_session.query(Project).filter(Project.id == pj_id).first()
                if pj in ws.projects:
                    return
                else:
                    raise NotFound("Project not found")
            return
        raise NotFound("Workspace not found")
    return
