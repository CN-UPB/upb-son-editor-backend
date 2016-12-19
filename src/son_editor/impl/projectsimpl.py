'''
Created on 05.08.2016

@author: Jonas
'''
import os
import shlex
import shutil
from subprocess import Popen, PIPE

from son_editor.app.database import db_session, scan_project_dir
from son_editor.app.exceptions import NotFound, NameConflict
from son_editor.impl import gitimpl
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import sync_project_descriptor
from son_editor.util.requestutil import CONFIG, rreplace

WORKSPACES_DIR = os.path.expanduser(CONFIG["workspaces-location"])
# make ws paths prettier
WORKSPACES_DIR = os.path.normpath(WORKSPACES_DIR)

def get_projects(ws_id: int) -> list:
    """
    Get a list of projects in this workspace
    :param ws_id:
    :return:
    """
    session = db_session()
    projects = session.query(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id).all()
    session.commit()
    return list(map(lambda x: x.as_dict(), projects))


def get_project(ws_id, pj_id):
    session = db_session()
    project = session.query(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == pj_id). \
        first()
    session.commit()
    if project:
        return project.as_dict()
    else:
        raise NotFound("No project with id {} could be found".format(pj_id))


def create_project(ws_id: int, project_data: dict) -> dict:
    """
    Create a new Project in this workspace
    :param ws_id:
    :param project_data:
    :return: The new project descriptor as a dict
    """
    project_name = shlex.quote(project_data["name"])
    repo = None
    if "repo" in project_data:
        repo = project_data["repo"]

    if repo:
        return gitimpl.clone(ws_id, repo, project_name)

    session = db_session()

    # test if ws Name exists in database

    workspace = session.query(Workspace). \
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
        set_data(project, project_data)

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
    """
    Update the Project
    :param project_data:
    :param project_id:
    :return:
    """
    session = db_session()
    project = session.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise NotFound("Project with id {} could not be found".format(project_id))

    # Update name
    if 'name' in project_data and project_data['name'] != project.name:
        if os.path.exists(get_project_path(project.workspace.path, project.rel_path)):
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
    set_data(project, project_data)
    sync_project_descriptor(project)
    db_session.commit()
    return project.as_dict()


def set_data(project: Project, project_data: dict) -> None:
    """
    Extracts the data from the dictionary and sets it on the database model
    :param project: The project database model
    :param project_data: The project data dictionary from the frontend
    :return:
    """
    if "description" in project_data:
        project.description = project_data['description']
    if "maintainer" in project_data:
        project.maintainer = project_data['maintainer']
    if "publish_to" in project_data:
        project.publish_to = ",".join(project_data['publish_to'])
    if "vendor" in project_data:
        project.vendor = project_data['vendor']
    if "version" in project_data:
        project.version = project_data['version']


def delete_project(project_id: int) -> dict:
    """
    Deletes the project from the database and from the Disk
    :param project_id: The id of the project to be deleted
    :return: The deleted project descriptor
    """
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


def get_project_path(workspace_path: str, rel_path: str) -> str:
    """
    Helper method to resolve the project path on disk for the given project
    :param workspace_path: the path to the workspace
    :param rel_path: the relative path of the project
    :return:
    """
    return os.path.join(workspace_path, "projects", rel_path)
