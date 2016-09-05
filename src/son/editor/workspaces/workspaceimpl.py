'''
Created on 25.07.2016

@author: Jonas
'''
import logging
import os
import shlex
import shutil
import tempfile
from subprocess import Popen, PIPE

from son.editor.app.database import db_session
from son.editor.app.exceptions import NameConflict, NotFound
from son.editor.app.util import CONFIG, rreplace
from son.editor.models.repository import Platform, Catalogue
from son.editor.models.workspace import Workspace
from son.editor.users.usermanagement import get_user

# If its testing, don't mess up workspace location
if CONFIG['testing']:
    WORKSPACES_DIR = tempfile.mkdtemp()
else:
    WORKSPACES_DIR = os.path.expanduser(CONFIG["workspaces-location"])

logger = logging.getLogger("son-editor.workspaceimpl")


def get_workspaces(user_data):
    session = db_session()
    user = get_user(user_data)
    workspaces = session.query(Workspace). \
        filter(Workspace.owner == user).all()
    session.commit()
    return list(map(lambda x: x.as_dict(), workspaces))


def get_workspace(user_data, ws_id):
    session = db_session()
    user = get_user(user_data)
    workspace = session.query(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id).first()
    session.commit()
    if workspace is not None:
        return workspace.as_dict()
    else:
        raise NotFound("No workspace with id " + ws_id + " exists")


def create_workspace(user_data, workspace_data):
    wsName = shlex.quote(workspace_data["name"])
    session = db_session()

    # test if ws Name exists in database
    user = get_user(user_data)

    existingWorkspaces = list(session.query(Workspace)
                              .filter(Workspace.owner == user)
                              .filter(Workspace.name == wsName))
    if len(existingWorkspaces) > 0:
        raise NameConflict("Workspace with name " + wsName + " already exists")

    wsPath = WORKSPACES_DIR + user.name + "/" + wsName
    # prepare db insert
    try:
        ws = Workspace(name=wsName, path=wsPath, owner=user)
        if 'platforms' in workspace_data:
            platforms = list(map(lambda x: Platform((x.name, ws, x.url)), workspace_data['platforms']))
            ws.platforms = platforms
        if 'catalogues' in workspace_data:
            catalogues = list(map(lambda x: Catalogue((x.name, ws, x.url)), workspace_data['catalogues']))
            ws.platforms = catalogues
        session.add(ws)
    except:
        logger.exception()
        session.rollback()
        raise
    # create workspace on disk
    proc = Popen(['son-workspace', '--init', '--workspace', wsPath], stdout=PIPE, stderr=PIPE)

    out, err = proc.communicate()
    exitcode = proc.returncode

    if out.decode().find('existing') >= 0:
        workspace_exists = True
    else:
        workspace_exists = False



    if exitcode == 0 and not workspace_exists:
        session.commit()
        return ws.as_dict()
    else:
        session.rollback()
        if workspace_exists:
            raise NameConflict(out.decode())
        raise Exception(err, out)


def update_workspace(workspace_Data, wsid):
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == int(wsid)).first()
    if workspace is None:
        raise NotFound("Workspace with id {} could not be found".format(wsid))

    # Update name
    if 'name' in workspace_Data:
        if os.path.exists(workspace.path):
            new_name = workspace_Data['name']
            old_path = workspace.path
            new_path = rreplace(workspace.path, workspace.name, new_name, 1)

            if os.path.exists(new_path):
                raise NameConflict("Invalid name parameter, workspace '{}' already exists".format(new_name))

            # Do not allow move directories outside of the workspaces_dir
            if not new_path.startswith(WORKSPACES_DIR):
                raise Exception("Invalid path parameter, you are not allowed to break out of {}".format(WORKSPACES_DIR))
            else:
                # Move the directory
                shutil.move(old_path, new_path)
                workspace.name = new_name
                workspace.path = new_path
    if 'platforms' in workspace_Data:
        platforms = list(map(lambda x: Platform((x.name, workspace, x.url)), workspace_Data['platforms']))
        workspace.platforms = platforms
    if 'catalogues' in workspace_Data:
        catalogues = list(map(lambda x: Catalogue((x.name, workspace, x.url)), workspace_Data['catalogues']))
        workspace.platforms = catalogues

    db_session.commit()
    return workspace.as_dict()


def delete_workspace(wsid):
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == int(wsid)).first()
    if workspace:
        path = workspace.path
        shutil.rmtree(path)
        session.delete(workspace)
    db_session.commit()
    if workspace:
        return workspace.as_dict()
    else:
        raise NotFound("Workspace with id {} was not found".format(wsid))
