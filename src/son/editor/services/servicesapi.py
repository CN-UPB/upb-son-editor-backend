'''
Created on 22.07.2016

@author: Jonas
'''
from flask import Blueprint
from flask.globals import request
from son.editor.app.constants import get_parent

services_api = Blueprint("services_api", __name__)  # , url_prefix='/workspaces/<wsID>/projects'

@services_api.route('/<parentID>/services', methods=['GET'])
def get_services(wsID, parentID):
    return "list of services in '" + str(get_parent(request)) + "' with id " + parentID


@services_api.route('/<parentID>/services', methods=['POST'])
def create_service(wsID, parentID):
    return "create new service in project"


@services_api.route('/<parentID>/services/<serviceID>', methods=['PUT'])
def update_service(wsID, parentID, serviceID):
    return "update service in project with id " + parentID


@services_api.route('/<parentID>/services/<serviceID>', methods=['DELETE'])
def delete_service(wsID, parentID, serviceID):
    return "deleted service from project with id " + parentID