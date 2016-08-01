'''
Created on 25.07.2016

@author: Jonas
'''
import os
import shlex
from subprocess import Popen, PIPE

from son.editor.app.database import db_session
from son.editor.app.util import CONFIG
from son.editor.models.workspace import Workspace


WORKSPACES_DIR = os.path.expanduser("~") + CONFIG["workspaces-location"]

def get_workspaces(user):
    session = db_session()
    return list(map(lambda x:x.as_dict(), session.query(Workspace).all()))


def create_workspace(user, workspaceData):
    # TODO: sanitize wsName because it is written to call
    wsName = shlex.quote(workspaceData["name"])
    session = db_session()

    # test if ws Name exists in database
    existingWorkspace = list(session.query(Workspace).filter(Workspace.name == wsName))
    if len(existingWorkspace) > 0:
        raise Exception("Workspace with name " + wsName + " already exists")

    wsPath = WORKSPACES_DIR + user + "/" + wsName
    proc = Popen(['son-workspace', '--init', '--workspace', wsPath], stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    if exitcode == 0:
        ws = Workspace(name=wsName, path=wsPath)
        session.add(ws)
        session.commit()
        return ws.as_dict()
    else:
        raise Exception(err, out)


