'''
Created on 22.07.2016

@author: Jonas
'''
import logging
from flask import Blueprint
from flask.globals import request
from son.editor.app.constants import get_parent
from son.editor.app.exceptions import NotFound, NameConflict
from son.editor.app.util import prepareResponse
from . import servicesimpl
from son.editor.app.util import getJSON

logger = logging.getLogger(__name__)

services_api = Blueprint("services_api", __name__)  # , url_prefix='/workspaces/<wsID>/projects'


@services_api.route('/<parentID>/services/', methods=['GET'])
def get_services(wsID, parentID):
    service = servicesimpl.get_services(wsID, parentID)
    return prepareResponse(service), 200


@services_api.route('/<parentID>/services/', methods=['POST'])
def create_service(wsID, parentID):
    service = servicesimpl.create_service(wsID, parentID)
    return prepareResponse(service), 201


@services_api.route('/<parentID>/services/<serviceID>', methods=['PUT'])
def update_service(wsID, parentID, serviceID):
    service = servicesimpl.update_service(wsID, parentID, serviceID)
    return prepareResponse(service), 200


@services_api.route('/<parentID>/services/<serviceID>', methods=['DELETE'])
def delete_service(wsID, parentID, serviceID):
    service = servicesimpl.delete_service(parentID, serviceID)
    return prepareResponse(service), 200
