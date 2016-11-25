import json
import logging
import os
import shlex
import shutil

import jsonschema
from jsonschema import ValidationError

from son_editor.app.database import db_session
from son_editor.app.exceptions import NameConflict, NotFound, InvalidArgument
from son_editor.impl.usermanagement import get_user
from son_editor.models.descriptor import Function
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import write_ns_vnf_to_disk, get_file_path, get_schema
from son.schema.validator import SchemaValidator

logger = logging.getLogger(__name__)


def get_functions(ws_id: int, project_id: int) -> list:
    """
    Get a list of all functions
    :param ws_id: The workspace ID
    :param project_id: The project id
    :return:
    """
    session = db_session()
    functions = session.query(Function).join(Project).join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Function.project_id == project_id).all()
    return list(map(lambda x: x.as_dict(), functions))


def get_function_project(ws_id: int, project_id: int, vnf_id: int) -> dict:
    """
    Get a single function from the specified project
    :param ws_id:
    :param project_id:
    :param vnf_id:
    :return:
    """
    session = db_session()
    function = session.query(Function).join(Project).join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Function.project_id == project_id). \
        filter(Function.id == vnf_id).first()
    return function.as_dict()


def create_function(ws_id: int, project_id: int, function_data: dict) -> dict:
    """
    Creates a new vnf in the project
    :param ws_id:
    :param project_id:
    :param function_data:
    :return: The created function as a dict
    """
    function_name = shlex.quote(function_data["name"])
    vendor_name = shlex.quote(function_data["vendor"])
    version = shlex.quote(function_data["version"])
    session = db_session()

    ws = session.query(Workspace).filter(Workspace.id == ws_id).first()  # type: Workspace
    schema = get_schema(ws.path, SchemaValidator.SCHEMA_FUNCTION_DESCRIPTOR)
    try:
        jsonschema.validate(function_data, schema)
    except ValidationError as ve:
        session.rollback()
        raise InvalidArgument("Validation failed: " + ve.message)

    # test if function Name exists in database
    existing_functions = list(session.query(Function)
                              .join(Project)
                              .join(Workspace)
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
        write_ns_vnf_to_disk("vnf", function)
    except:
        logger.exception("Could not write data to disk:")
        session.rollback()
        raise
    session.commit()
    return function.as_dict()


def update_function(ws_id: int, prj_id: int, func_id: int, func_data: dict) -> dict:
    """
    Update the function descriptor
    :param ws_id:
    :param prj_id:
    :param func_id:
    :param func_data:
    :return: The updated function descriptor
    """
    session = db_session()

    ws = session.query(Workspace).filter(Workspace.id == ws_id).first()  # type: Workspace
    schema = get_schema(ws.path, SchemaValidator.SCHEMA_FUNCTION_DESCRIPTOR)
    try:
        jsonschema.validate(func_data, schema)
    except ValidationError as ve:
        session.rollback()
        raise InvalidArgument("Validation failed: " + ve.message)

    # test if ws Name exists in database
    function = session.query(Function). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == prj_id). \
        filter(Function.id == func_id).first()
    if function is None:
        session.rollback()
        raise NotFound("Function with id {} does not exist".format(func_id))
    function.descriptor = json.dumps(func_data)

    old_file_name = get_file_path("vnf", function)
    if 'name' in func_data:
        function.name = shlex.quote(func_data["name"])
    if 'vendor' in func_data:
        function.vendor = shlex.quote(func_data["vendor"])
    if 'version' in func_data:
        function.version = shlex.quote(func_data["version"])
    try:
        new_file_name = get_file_path("vnf", function)
        if not new_file_name == old_file_name:
            shutil.move(old_file_name, new_file_name)
        write_ns_vnf_to_disk("vnf", function)
    except:
        session.rollback()
        logger.exception("Could not update descriptor file:")
        raise
    session.commit()
    return function.as_dict()


def delete_function(ws_id: int, project_id: int, function_id: int) -> dict:
    """
    Deletes the function
    :param ws_id:
    :param project_id:
    :param function_id:
    :return: the deleted function
    """
    session = db_session()
    function = session.query(Function). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == project_id). \
        filter(Function.id == function_id).first()
    if function is not None:
        session.delete(function)
    else:
        session.rollback()
        raise NotFound("Function with id " + function_id + " does not exist")
    try:
        os.remove(get_file_path("vnf", function))
    except:
        session.rollback()
        logger.exception("Could not delete function:")
        raise
    session.commit()
    return function.as_dict()
