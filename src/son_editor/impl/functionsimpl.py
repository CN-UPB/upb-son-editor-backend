import json
import logging
import os
import shlex
import shutil
from pathlib import Path

import jsonschema
from jsonschema import ValidationError
from werkzeug.utils import secure_filename

from son_editor.app.database import db_session
from son_editor.app.exceptions import NameConflict, NotFound, InvalidArgument
from son_editor.models.descriptor import Function
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import write_ns_vnf_to_disk, get_file_path, get_schema, get_file_name, SCHEMA_ID_VNF

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
    try:
        function_name = shlex.quote(function_data["name"])
        vendor_name = shlex.quote(function_data["vendor"])
        version = shlex.quote(function_data["version"])
    except KeyError as ke:
        raise InvalidArgument("Missing key {} in function data".format(str(ke)))

    session = db_session()

    ws = session.query(Workspace).filter(Workspace.id == ws_id).first()  # type: Workspace
    validate_vnf(ws.vnf_schema_index, function_data)

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

    ws = session.query(Workspace).filter(Workspace.id == ws_id).first()
    validate_vnf(ws.vnf_schema_index, func_data)

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
    old_folder_path = old_file_name.replace(get_file_name(function), "")
    try:
        function.name = shlex.quote(func_data["name"])
        function.vendor = shlex.quote(func_data["vendor"])
        function.version = shlex.quote(func_data["version"])
    except KeyError as ke:
        session.rollback()
        raise InvalidArgument("Missing key {} in function data".format(str(ke)))

    try:
        new_file_name = get_file_path("vnf", function)
        new_folder_path = new_file_name.replace(get_file_name(function), "")
        if old_folder_path != new_folder_path:
            # move old files to new location
            os.makedirs(new_folder_path)
            for file in os.listdir(old_folder_path):
                if not old_file_name == os.path.join(old_folder_path, file):  # don't move descriptor yet
                    shutil.move(os.path.join(old_folder_path, file), os.path.join(new_folder_path, file))
        if not new_file_name == old_file_name:
            shutil.move(old_file_name, new_file_name)
        if old_folder_path != new_folder_path:
            # cleanup old folder
            shutil.rmtree(old_folder_path)
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


def validate_vnf(schema_index: int, descriptor: dict) -> None:
    schema = get_schema(schema_index, SCHEMA_ID_VNF)
    try:
        jsonschema.validate(descriptor, schema)
    except ValidationError as ve:
        raise InvalidArgument("Validation failed: <br/> Path: {} <br/> Error: {}".format(list(ve.path), ve.message))


def save_image_file(ws_id, project_id, function_id, file):
    if file.filename == '':
        raise InvalidArgument("No file attached!")
    if file:
        filename = secure_filename(file.filename)
        session = db_session()
        function = session.query(Function). \
            join(Project). \
            join(Workspace). \
            filter(Workspace.id == ws_id). \
            filter(Project.id == project_id). \
            filter(Function.id == function_id).first()
        if function is not None:
            file_path = get_file_path("vnf", function)
            file_path = file_path.replace(get_file_name(function), filename)
            file.save(file_path)
            return "File {} successfully uploaded!".format(filename)
        else:
            raise NotFound("Function with id " + function_id + " does not exist")


def get_image_files(ws_id, project_id, function_id):
    session = db_session()
    function = session.query(Function). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == project_id). \
        filter(Function.id == function_id).first()
    if function:
        folder_path = get_file_path("vnf", function).replace(get_file_name(function), "")
        image_files = []

        for filename in os.listdir(folder_path):
            if not Path(os.path.join(folder_path, filename)).is_dir():
                if not filename == get_file_name(function):
                    image_files.append(filename)
        return image_files
    else:
        raise NotFound("Function with id " + function_id + " does not exist")


def delete_image_file(ws_id, project_id, vnf_id, filename):
    session = db_session()
    function = session.query(Function). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == project_id). \
        filter(Function.id == vnf_id).first()
    if function:
        save_name = secure_filename(filename)
        if not save_name == get_file_name(function):
            file_path = get_file_path("vnf", function).replace(get_file_name(function), save_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                return "File {} was deleted".format(save_name)
            else:
                raise NotFound("File {} not found!".format(save_name))
    else:
        raise NotFound("Function with id " + vnf_id + " does not exist")
