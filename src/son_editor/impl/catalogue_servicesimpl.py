import json

import requests

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound
from son_editor.models.descriptor import Function, Service
from son_editor.models.repository import Catalogue

# Catalogue methods

# Define catalogue url suffix for get / post to list / create network services
NS_PREFIX = "network-services"
VNF_PREFIX = "vnfs"
CATALOGUE_SPECIFIC_URL = "/{type}/vendor/{vendor}/name/{name}/version/{version}"
CATALOGUE_LIST_CREATE_SUFFIX = "/{type}"

# Timeout of HTTP requests in seconds
TIMEOUT = 5


## Some helper functions

def getType(is_vnf:bool)->str:
    """
    Returns the vnf / ns prefix
    :param is_vnf:
    :return: the prefix for the type
    """
    if is_vnf:
        return VNF_PREFIX
    else:
        return NS_PREFIX


def get_catalogue(catalogue_id):
    """
    Retrieves a catalogue by given id
    :param catalogue_id: int
    :return:
    """
    session = db_session()
    catalogue = session.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    # Check if catalogue exists
    if not catalogue:
        raise NotFound("Catalogue with id '{}' could not be found".format(catalogue_id))
    return catalogue


def get_service(service_id):
    """Returns a service with the given service id"""
    session = db_session()
    service = session.query(Service).filter(Service.id == service_id).first()
    # Check if the function could be retrieved
    if not service:
        raise NotFound("Service with id '{}' does not exist".format(service_id))
    return service


def get_function(function_id):
    """ Returns a function with the given function id"""
    session = db_session()
    function = session.query(Function).filter(Function.id == function_id).first()
    # Check if the function could be retrieved
    if not function:
        raise NotFound("Function with id '{}' does not exist".format(function_id))
    return function


def createID(e: dict):
    """
    Expects a dict type with name, vendor, version
    :param e: dict with name, vendor, version
    :return: the id of the descriptor
    """
    return e['name'] + ":" + e['vendor'] + ":" + e['version']


def decodeID(id)->tuple:
    """
    Returns the parts of a given id
    :param id:
    :return: tuple of name, vendor , version
    """
    list = str.split(id, ":")
    return list[0], list[1], list[2]


def build_URL(is_vnf, name, vendor, version):
    """
    builds the url from the given name vendor and version
    :param is_vnf:
    :param name:
    :param vendor:
    :param version:
    :return:
    """
    service_url = CATALOGUE_SPECIFIC_URL.replace("{type}", getType(is_vnf))
    service_url = service_url.replace('{vendor}', vendor)
    service_url = service_url.replace('{name}', name)
    service_url = service_url.replace('{version}', version)
    return service_url


## Actual catalogue HTTP actions

def create_in_catalogue(user_data, catalogue_id, function_id, is_vnf):
    """
    Creates a function on the catalogue
    :param user_data:
    :param catalogue_id:
    :param function_id:
    :param is_vnf:
    :return:
    """
    url_suffix = CATALOGUE_LIST_CREATE_SUFFIX.replace("{type}", getType(is_vnf))
    if is_vnf:
        function = get_function(function_id)
    else:
        function = get_service(function_id)
    catalogue = get_catalogue(catalogue_id)

    # Create network service on the catalogue
    response = requests.post(catalogue.url + url_suffix, json=json.loads(function.descriptor), timeout=TIMEOUT)
    if response.status_code != 201 and response.status_code != 200:
        raise Exception("External service '{}' delivered unexpected status code '{}', reason: {}".format(
            catalogue.url + url_suffix, response.status_code, response.text))
    return json.loads(response.text)


def get_all_in_catalogue(user_data, ws_id, catalogue_id, is_vnf):
    """
    Retrieves a list of catalogue functions
    :param user_data:
    :param ws_id:
    :param catalogue_id:
    :param is_vnf:
    :return:
    """
    url_suffix = CATALOGUE_LIST_CREATE_SUFFIX.replace("{type}", getType(is_vnf))
    catalogue = get_catalogue(catalogue_id)

    # Retrieve network services
    response = requests.get(catalogue.url + url_suffix, headers={'content-type': 'application/json'}, timeout=TIMEOUT)
    function_list = json.loads(response.text)

    # Append an id to the elements, it consists of name,vendor,version
    for function in function_list:
        function['id'] = createID(function)

    if response.status_code != 200:
        raise Exception("External service '{}' delivered unexpected status code '{}', reason: {}".format(
            catalogue.url + url_suffix, response.status_code, response.text))

    return function_list


def get_in_catalogue(ws_id, catalogue_id, function_id, is_vnf):
    """
    Gets a specific function
    :param ws_id:
    :param catalogue_id:
    :param function_id:
    :param is_vnf:
    :return:
    """
    name, vendor, version = decodeID(function_id)
    catalogue = get_catalogue(catalogue_id)

    service_url = build_URL(is_vnf, name, vendor, version)

    response = requests.get(catalogue.url + service_url, headers={'content-type': 'application/json'}, timeout=TIMEOUT)
    return json.loads(response.text)


def update_service_catalogue(ws_id, catalogue_id, function_id, function_data, is_vnf):
    """ Update the service in the catalogue
    :param ws_id:
    :param catalogue_id:
    :param function_id:
    :param function_data:
    :param is_vnf:
    :return:
    """
    name, vendor, version = decodeID(function_id)
    catalogue = get_catalogue(catalogue_id)

    service_url = build_URL(is_vnf, name, vendor, version)
    function_data = function_data.copy()
    if not is_vnf:
        function_data = function_data["descriptor"]

    response = requests.put(catalogue.url + service_url, json=function_data, timeout=TIMEOUT)
    if response.status_code != 200:
        raise Exception(
            "External service '{}' delivered unexpected status code '{}', reason: {}".format(
                catalogue.url + service_url, response.status_code, response.text))


def delete_service_catalogue(ws_id, catalogue_id, function_id, is_vnf):
    """
    Delete the service in the catalogue
    :param ws_id:
    :param catalogue_id:
    :param function_id:
    :param is_vnf:
    :return:
    """
    name, vendor, version = decodeID(function_id)
    catalogue = get_catalogue(catalogue_id)

    service_url = build_URL(is_vnf, name, vendor, version)

    response = requests.delete(catalogue.url + service_url, timeout=TIMEOUT)
    if response.status_code != 200:
        raise Exception(
            "External service '{}' delivered unexpected status code '{}, reason: {}".format(catalogue.url + service_url,
                                                                                            response.status_code,
                                                                                            response.text))
