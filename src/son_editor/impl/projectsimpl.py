'''
Created on 05.08.2016

@author: Jonas
'''
import os
import shlex
import shutil
import tempfile
from subprocess import Popen, PIPE

from son_editor.app.database import db_session, scan_project_dir
from son_editor.app.exceptions import NotFound, NameConflict
from son_editor.impl.usermanagement import get_user
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import sync_project_descriptor
from son_editor.util.requestutil import CONFIG, rreplace

if CONFIG['testing']:
    WORKSPACES_DIR = tempfile.mkdtemp()
else:
    WORKSPACES_DIR = os.path.expanduser(CONFIG["workspaces-location"])


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
    if project:
        return project.as_dict()
    else:
        raise NotFound("No project with id {} could be found".format(pj_id))


def create_project(user_data, ws_id, project_data):
    project_name = shlex.quote(project_data["name"])
    session = db_session()

    # test if ws Name exists in database
    user = get_user(user_data)

    workspace = session.query(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id).first()
    if workspace is None:
        raise NotFound("No workspace with id {} was found".format(ws_id))

    existing_projects = list(session.query(Project)
                             .filter(Project.workspace == workspace)
                             .filter(Project.name == project_name))
    if len(existing_projects) > 0:
        raise NameConflict("Project with name '{}' already exists in this workspace".format(project_name))

    # prepare db insert
    try:
        project = Project(name=project_name, rel_path=project_name, workspace=workspace)
        if "description" in project_data:
            project.description = project_data['description']
        if "maintainer" in project_data:
            project.maintainer = project_data['maintainer']
        if "publish_to" in project_data:
            project.publish_to = ','.join(project_data['publish_to'])
        if "vendor" in project_data:
            project.vendor = project_data['vendor']
        if "version" in project_data:
            project.version = project_data['version']
        else:
            project.version = "0.1"

        session.add(project)
    except:
        session.rollback()
        raise
    # create workspace on disk
    proc = Popen(['son-workspace',
                  '--workspace', workspace.path,
                  '--project', get_project_path(workspace.path, project_name)],
                 stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode

    if err.decode().find('exists') >= 0:
        project_exists = True
    else:
        project_exists = False

    if exitcode == 0 and not project_exists:
        sync_project_descriptor(project)
        session.commit()
        scan_project_dir(get_project_path(workspace.path, project_name), project)
        return project.as_dict()
    else:
        session.rollback()
        if project_exists:
            raise NameConflict("Project with name '{}' already exists in this workspace".format(project_name))
        raise Exception(err.decode(), out.decode())


def update_project(project_data, project_id):
    session = db_session()
    project = session.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise NotFound("Project with id {} could not be found".format(project_id))

    # Update name
    if 'name' in project_data:
        if os.path.exists(project.path):
            new_name = shlex.quote(project_data['name'])
            old_path = get_project_path(project.workspace.path, project.rel_path)
            new_path = rreplace(old_path, project.name, new_name, 1)

            if os.path.exists(new_path):
                raise NameConflict("Invalid name parameter, workspace '{}' already exists".format(new_name))

            # Do not allow move directories outside of the workspaces_dir
            if not new_path.startswith(WORKSPACES_DIR):
                raise Exception("Invalid path parameter, you are not allowed to break out of {}".format(WORKSPACES_DIR))
            else:
                # Move the directory
                shutil.move(old_path, new_path)
                project.name = new_name
                project.rel_path = new_name
    if "description" in project_data:
        project.description = project_data['description']
    if "maintainer" in project_data:
        project.maintainer = project_data['maintainer']
    if "publish_to" in project_data:
        project.publish_to = str(project_data['publish_to'])
    if "vendor" in project_data:
        project.vendor = project_data['vendor']
    if "version" in project_data:
        project.version = project_data['version']
    sync_project_descriptor(project)
    db_session.commit()
    return project.as_dict()


def delete_project(project_id):
    session = db_session()
    project = session.query(Project).filter(Project.id == int(project_id)).first()
    if project:
        path = get_project_path(project.workspace.path, project.rel_path)
        shutil.rmtree(path)
        session.delete(project)
    db_session.commit()
    if project:
        return project.as_dict()
    else:
        raise NotFound("Project with id {} was not found".format(project_id))


def get_project_path(workspace_path, rel_path):
    return os.path.join(workspace_path, "projects", rel_path)
