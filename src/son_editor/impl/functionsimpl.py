import json
import shlex
import requests

from son_editor.app.database import db_session
from son_editor.app.exceptions import NameConflict, NotFound, ExtNotReachable
from son_editor.impl.usermanagement import get_user
from son_editor.models.function import Function
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.models.repository import Catalogue


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


# Creates a function on the catalogue
def create_function_catalogue(user_data, ws_id, catalogue_id, function_data):
    function_name = shlex.quote(function_data["name"])
    vendor_name = shlex.quote(function_data["vendor"])
    version = shlex.quote(function_data["version"])
    session = db_session()

    catalogue = session.query(Catalogue).filter(Catalogue.id == catalogue_id).first()

    # Check if the given catalogue exists
    if not catalogue:
        raise NotFound("Catalogue with id {} does not exist".format(catalogue_id))

    # Test if function Name exists in database
    getRequest = get_functions_catalogue(user_data, ws_id, catalogue_id)
    for element in getRequest:
        if element and "name" in element and "vendor" in element and "version" in element:
            if element['name'] == function_name and element['vendor'] == vendor_name and element['version'] == version:
                raise NameConflict("Function already exists in catalogue {}".format(catalogue_id))

    # Create network service
    response = requests.post(catalogue.url + CATALOGUE_LISTCREATE_SUFFIX, json=json.dumps(function_data))
    return response.data
