'''
Created on 22.07.2016

@author: Jonas
'''
from flask import Blueprint
from flask.globals import request
from son.editor.app.constants import get_parent
from son.editor.app.util import prepareResponse
from . import servicesimpl

services_api = Blueprint("services_api", __name__)  # , url_prefix='/workspaces/<wsID>/projects'

@services_api.route('/<parentID>/services/', methods=['GET'])
def get_services(wsID, parentID):
    services = {"services":[{"name":"service1", "id":1, "description":"blalalblaald"}]}
    return prepareResponse(services)


@services_api.route('/<parentID>/services/', methods=['POST'])
def create_service(wsID, parentID):
    return servicesimpl.create_service(wsID, parentID)


@services_api.route('/<parentID>/services/<serviceID>', methods=['PUT'])
def update_service(wsID, parentID, serviceID):
    return servicesimpl.update_service(wsID,parentID, serviceID)


@services_api.route('/<parentID>/services/<serviceID>', methods=['DELETE'])
def delete_service(wsID, parentID, serviceID):
    return servicesimpl.delete_service(wsID, parentID,serviceID)