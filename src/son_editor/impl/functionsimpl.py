import json
import logging
import os
import shlex
import shutil

from son_editor.app.database import db_session
from son_editor.app.exceptions import NameConflict, NotFound
from son_editor.impl.usermanagement import get_user
from son_editor.models.descriptor import Function
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import write_to_disk, get_file_name

logger = logging.getLogger(__name__)


def get_functions(user_data, ws_id, project_id):
    user = get_user(user_data)
    session = db_session()
    functions = session.query(Function).join(Project).join(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id). \
        filter(Function.project_id == project_id).all()
    return list(map(lambda x: x.as_dict(), functions))


def get_function_project(user_data, ws_id, project_id, vnf_id):
    user = get_user(user_data)
    session = db_session()
    function = session.query(Function).join(Project).join(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id). \
        filter(Function.project_id == project_id). \
        filter(Function.id == vnf_id).first()
    return function.as_dict()


def create_function(user_data, ws_id, project_id, function_data):
    function_name = shlex.quote(function_data["name"])
    vendor_name = shlex.quote(function_data["vendor"])
    version = shlex.quote(function_data["version"])
    session = db_session()

    # test if function Name exists in database
    user = get_user(user_data)
    existing_functions = list(session.query(Function)
                              .join(Project)
                              .join(Workspace)
                              .filter(Workspace.owner == user)
                              .filter(Workspace.id == ws_id)
                              .filter(Function.project_id == project_id)
                              .filter(Function.name == function_name))
    if len(existing_functions) > 0:
        raise NameConflict("Function with name " + function_name + " already exists")
    project = session.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise NotFound("No project with id " + project_id + " was found")
    function = Function(name=function_name,
                        project=project,
                        vendor=vendor_name,
                        version=version,
                        descriptor=json.dumps(function_data))
    session.add(function)
    try:
        write_to_disk("vnf", function)
    except:
        logger.exception("Could not write data to disk:")
        session.rollback()
        raise
    session.commit()
    return function.as_dict()


def update_function(user_data, ws_id, project_id, function_id, function_data):
    session = db_session()

    # test if ws Name exists in database
    user = get_user(user_data)
    function = session.query(Function). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == project_id). \
        filter(Function.id == function_id).first()
    if function is None:
        session.rollback()
        raise NotFound("Function with id " + function_id + " does not exist")
    function.descriptor = json.dumps(function_data)
    old_file_name = get_file_name("vnf", function)
    if 'name' in function_data:
        function.name = shlex.quote(function_data["name"])
    if 'vendor' in function_data:
        function.vendor = shlex.quote(function_data["vendor"])
    if 'version' in function_data:
        function.version = shlex.quote(function_data["version"])
    try:
        new_file_name = get_file_name("vnf", function)
        if not new_file_name == old_file_name:
            shutil.move(old_file_name, new_file_name)
        write_to_disk("vnf", function)
    except:
        session.rollback()
        logger.exception("Could not update descriptor file:")
        raise
    session.commit()
    return function.as_dict()


def delete_function(user_data, ws_id, project_id, function_id):
    session = db_session()
    user = get_user(user_data)
    function = session.query(Function). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == project_id). \
        filter(Function.id == function_id).first()
    if function is not None:
        session.delete(function)
    else:
        session.rollback()
        raise NotFound("Function with id " + function_id + " does not exist")
    try:
        os.remove(get_file_name("vnf", function))
    except:
        session.rollback()
        logger.exception("Could not delete function:")
        raise
    session.commit()
    return function.as_dict()



