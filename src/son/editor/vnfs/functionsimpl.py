import json
import logging
import os
import shlex
import platform

from subprocess import Popen, PIPE
from sys import platform

from son.editor.app.database import db_session
from son.editor.app.exceptions import NameConflict, NotFound
from son.editor.app.util import CONFIG
from son.editor.models.function import Function, FunctionEncoder
from son.editor.models.project import Project
from son.editor.models.workspace import Workspace
from son.editor.users.usermanagement import get_user


def get_functions(user_data, ws_id, project_id):
    ws_id = shlex.quote(ws_id)
    project_id = shlex.quote(project_id)
    user = get_user(user_data)
    session = db_session()
    functions = session.query(Function).join(Project).join(Workspace). \
        filter(Workspace.owner == user). \
        filter(Workspace.id == ws_id). \
        filter(Function.project_id == project_id).all()
    return list(map(lambda x: x.as_dict(), functions))


def create_function(user_data, ws_id, project_id, function_data):
    ws_id = shlex.quote(ws_id)
    project_id = shlex.quote(project_id)
    function_name = shlex.quote(function_data["name"])
    vendor_name = shlex.quote(function_data["vendor"])
    version = shlex.quote(function_data["version"])
    session = db_session()

    # test if ws Name exists in database
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
        raise NotFound("Function with id " + function_id + " does not exist")
    function.descriptor = json.dumps(function_data)
    if 'name' in function_data:
        function.name = shlex.quote(function_data['name'])
    if 'vendor' in function_data:
        function.vendor = shlex.quote(function_data['vendor'])
    if 'version' in function_data:
        function.version = shlex.quote(function_data['version'])

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
        session.commit()
    else:
        raise NotFound("Function with id " + function_id + " does not exist")
    return function.as_dict()
