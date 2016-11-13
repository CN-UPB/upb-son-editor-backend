'''
Created on 25.07.2016

@author: Jonas
'''
import logging
from os import path
import shlex
import shutil
from subprocess import Popen, PIPE

import yaml

from son_editor.app.database import db_session
from son_editor.app.exceptions import NameConflict, NotFound, InvalidArgument
from son_editor.impl.usermanagement import get_user
from son_editor.models.repository import Platform, Catalogue
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import synchronize_workspace_descriptor, update_workspace_descriptor
from son_editor.util.requestutil import CONFIG, rreplace

WORKSPACES_DIR = path.expanduser(CONFIG["workspaces-location"])
# make ws paths prettier
WORKSPACES_DIR = path.normpath(WORKSPACES_DIR)

logger = logging.getLogger(__name__)


def get_workspaces(user_data: dict) -> list:
    """
    Get all workspaces for the current user
    :param user_data: the data identifying the user
    :return: A list wof workspace dictionaries
    """
    session = db_session()
    user = get_user(user_data)
    workspaces = session.query(Workspace). \
        filter(Workspace.owner == user).all()
    session.commit()
    return list(map(lambda x: x.as_dict(), workspaces))


def get_workspace(ws_id: int) -> dict:
    """
    Get a workspace by ID
    :param ws_id:
    :return: A dictionary wich contains the Workspace configuration
    """
    session = db_session()
    workspace = session.query(Workspace). \
        filter(Workspace.id == ws_id).first()
    session.commit()
    if workspace is not None:
        return workspace.as_dict()
    else:
        raise NotFound("No workspace with id " + ws_id + " exists")


def create_workspace(user_data: dict, workspace_data: dict) -> dict:
    """
    Creates a workspace (on disk and in the database) from the given workspace data
    :param user_data: The data identifiying the User
    :param workspace_data: The workspace configuration data
    :return: The created workspace
    """
    wsName = shlex.quote(workspace_data["name"])
    session = db_session()

    # test if ws Name exists in database
    user = get_user(user_data)

    existingWorkspaces = list(session.query(Workspace)
                              .filter(Workspace.owner == user)
                              .filter(Workspace.name == wsName))
    if len(existingWorkspaces) > 0:
        raise NameConflict("Workspace with name " + wsName + " already exists")

    wsPath = path.join(WORKSPACES_DIR, user.name, wsName)
    # prepare db insert
    try:
        ws = Workspace(name=wsName, path=wsPath, owner=user)
        session.add(ws)
        if 'platforms' in workspace_data:
            for platform in workspace_data['platforms']:
                session.add(Platform(platform['name'], platform['url'], ws))
        if 'catalogues' in workspace_data:
            for catalogue in workspace_data['catalogues']:
                session.add(Catalogue(catalogue['name'], catalogue['url'], ws))
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
        synchronize_workspace_descriptor(ws, session)
        session.commit()
        return ws.as_dict()
    else:
        session.rollback()
        if workspace_exists:
            raise NameConflict(out.decode())
        raise Exception(err, out)


def update_workspace(workspace_data, wsid):
    """
    Updates the workspace with the given workspace data
    :param workspace_data: The new workspace configuration
    :param wsid: the workspace ID
    :return: The updated workspace
    """
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == int(wsid)).first()  # type: Workspace
    if workspace is None:
        raise NotFound("Workspace with id {} could not be found".format(wsid))

    # Update name
    if 'name' in workspace_data:
        if path.exists(workspace.path):
            new_name = workspace_data['name']
            old_path = workspace.path
            # only update if name has changed
            if new_name != workspace.name:
                new_path = rreplace(workspace.path, workspace.name, new_name, 1)

                if path.exists(new_path):
                    raise NameConflict("Invalid name parameter, workspace '{}' already exists".format(new_name))

                # Do not allow move directories outside of the workspaces_dir
                if not new_path.startswith(WORKSPACES_DIR):
                    raise Exception(
                        "Invalid path parameter, you are not allowed to break out of {}".format(WORKSPACES_DIR))
                else:
                    # Move the directory
                    shutil.move(old_path, new_path)
                    workspace.name = new_name
                    workspace.path = new_path
    for platform in workspace.platforms:
        deleted = True
        if 'platforms' in workspace_data:
            for updated_platform in workspace_data['platforms']:
                if 'id' in updated_platform and platform.id == updated_platform['id']:
                    deleted = False
                    break
        if deleted:
            session.delete(platform)
    if 'platforms' in workspace_data:
        for updated_platform in workspace_data['platforms']:
            platform = None
            if 'id' in updated_platform:
                platform = session.query(Platform). \
                    filter(Platform.id == updated_platform['id']). \
                    filter(Platform.workspace == workspace). \
                    first()
            if platform:
                # update existing
                platform.name = updated_platform['name']
                platform.url = updated_platform['url']
            else:
                # create new
                new_platform = Platform(updated_platform['name'], updated_platform['url'], True, workspace)
                session.add(new_platform)
    for catalogue in workspace.catalogues:
        deleted = True
        if 'catalogues' in workspace_data:
            for updated_catalogue in workspace_data['catalogues']:
                if 'id' in updated_catalogue and catalogue.id == updated_catalogue['id']:
                    deleted = False
                    break
        if deleted:
            # check if catalogue is still referenced
            for project in workspace.projects:
                if catalogue.name in project.publish_to:
                    raise InvalidArgument(
                        "Cannot delete catalogue '{}' because it is still used in project '{}'!".format(catalogue.name,
                                                                                                       project.name))
            session.delete(catalogue)
    if 'catalogues' in workspace_data:
        for updated_catalogue in workspace_data['catalogues']:
            catalogue = None
            if 'id' in updated_catalogue:
                catalogue = session.query(Catalogue). \
                    filter(Catalogue.id == updated_catalogue['id']). \
                    filter(Catalogue.workspace == workspace). \
                    first()
            if catalogue:
                # update existing
                catalogue.name = updated_catalogue['name']
                catalogue.url = updated_catalogue['url']
            else:
                # create new
                new_catalogue = Catalogue(updated_catalogue['name'], updated_catalogue['url'], True, workspace)
                session.add(new_catalogue)
    update_workspace_descriptor(workspace)
    db_session.commit()
    return workspace.as_dict()


def delete_workspace(wsid):
    """
    Deletes the workspace from the database and from disk
    :param wsid: The workspace ID
    :return: The deleted workspace
    """
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
