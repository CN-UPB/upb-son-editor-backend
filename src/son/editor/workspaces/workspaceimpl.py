'''
Created on 25.07.2016

@author: Jonas
'''
import logging
import os
import shlex
import platform

from subprocess import Popen, PIPE
from sys import platform

from son.editor.app.database import db_session
from son.editor.app.util import CONFIG
from son.editor.models.workspace import Workspace
from son.editor.users.usermanagement import get_user

WORKSPACES_DIR = os.path.expanduser("~") + CONFIG["workspaces-location"]
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
        raise Exception("No workspace with id " + ws_id + " exists")


def create_workspace(user_data, workspaceData):
    wsName = shlex.quote(workspaceData["name"])
    session = db_session()

    # test if ws Name exists in database
    user = get_user(user_data)

    existingWorkspaces = list(session.query(Workspace)
                              .filter(Workspace.owner == user)
                              .filter(Workspace.name == wsName))
    if len(existingWorkspaces) > 0:
        raise Exception("Workspace with name " + wsName + " already exists")

    wsPath = WORKSPACES_DIR + user.name + "/" + wsName
    #prepare db insert
    try:
        ws = Workspace(name=wsName, path=wsPath, owner=user)
        session.add(ws)
    except:
        logger.exception()
        session.rollback
        raise
    #create workspace on disk
    proc = Popen(['son-workspace', '--init', '--workspace', wsPath], stdout=PIPE, stderr=PIPE)

    out, err = proc.communicate()
    exitcode = proc.returncode
    if exitcode == 0:
        session.commit()
        return ws.as_dict()
    else:
        session.rollback()
        raise Exception(err, out)
