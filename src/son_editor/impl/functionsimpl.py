import json
import os
import shlex
import logging

import shutil
import requests

from son_editor.app.database import db_session
from son_editor.app.exceptions import NameConflict, NotFound, ExtNotReachable
from son_editor.impl.usermanagement import get_user
from son_editor.models.descriptor import Function
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import write_to_disk, get_file_name
from son_editor.models.repository import Catalogue

logger = logging.getLogger("son-editor.functionsimpl")


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


# Catalogue methods

# Define catalogue url suffix for get / post to list / create network services
CATALOGUE_LISTCREATE_SUFFIX = "/network-services"


# Retrieves a list of catalogue functions
def get_functions_catalogue(user_data, ws_id, catalogue_id):
    session = db_session()
    catalogue = session.query(Catalogue).filter(Catalogue.id == catalogue_id).first()

    # Check if catalogue exists
    if not catalogue:
        raise NotFound("Catalogue with id {} could not be found".format(catalogue_id))

    response = requests.get(catalogue.url + CATALOGUE_LISTCREATE_SUFFIX, headers={'content-type': 'application/json'})
    if response.status_code != 200:
        raise ExtNotReachable("External service with URL {} does not delivered valid data".format(
            catalogue.url + CATALOGUE_LISTCREATE_SUFFIX))
    return json.dumps(response.content)


def get_function_catalogue(user_id, ws_id, function_uid):
    return None


def update_function_catalogue(user_data, ws_id, catalogue_id, function_data):
    return None


# Creates a function on the catalogue
def create_function_catalogue(user_data, ws_id, catalogue_id, function_id):
    session = db_session()

    function = session.query(Function).filter(Function.id == function_id)
    catalogue = session.query(Catalogue).filter(Catalogue.id == catalogue_id).first()

    if not function:
        raise NotFound("Function with id {} does not exist".format(function_id))
    # Check if the given catalogue exists
    if not catalogue:
        raise NotFound("Catalogue with id {} does not exist".format(catalogue_id))

    # Test if function Name exists in catalogue
    function_data = get_function_catalogue(user_data, ws_id, function)

    # Function exists on remote, update
    response = requests.post(catalogue.url + CATALOGUE_LISTCREATE_SUFFIX, json=json.dumps(function))


    # Create network service

    return response.data
