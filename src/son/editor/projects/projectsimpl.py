'''
Created on 05.08.2016

@author: Jonas
'''
import os
import shlex
from subprocess import Popen, PIPE

from son.editor.app.database import db_session
from son.editor.app.util import CONFIG
from son.editor.models.user import User
from son.editor.models.workspace import Workspace
from son.editor.models.project import Project
from son.editor.users.usermanagement import get_user


def get_projects(user_data, ws_id):
    user = get_user(user_data)

    session = db_session()
    projects = session.query(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Workspace.owner == user).all()
    session.commit()
    return list(map(lambda x: x.as_dict(), projects))


def get_project(user_data, ws_id, pj_id):
    user = get_user(user_data)

    session = db_session()
    project = session.query(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Workspace.owner == user). \
        filter(Project.id == pj_id). \
        first()
    session.commit()
    return project.as_dict()


def create_project(user_data, ws_id, project_data):
    project_name = shlex.quote(project_data["name"])
    session = db_session()

    # test if ws Name exists in database
    user = get_user(user_data)

    workspace = session.query(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id).first()
    if workspace is None:
        raise Exception("No workspace with id %s was found for this user" % ws_id)

    existing_projects = list(session.query(Project)
                             .filter(Project.workspace_id == workspace)
                             .filter(Project.name == project_name))
    if len(existing_projects) > 0:
        raise Exception("Project with name %s already exists in this workspace" % project_name)

    # prepare db insert
    try:
        project = Project(name=project_name, rel_path=project_name)
        session.add(project)
    except:
        session.rollback
        raise
    # create workspace on disk
    proc = Popen(['son-workspace',
                  '--workspace', workspace.path,
                  '--project', '{}/projects/{}'.format(workspace.path, project_name)],
                 stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    if exitcode == 0:
        session.commit()
        return project.as_dict()
    else:
        session.rollback()
        raise Exception(err, out)
