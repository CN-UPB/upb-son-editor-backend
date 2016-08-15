'''
Created on 22.07.2016

@author: Jonas
'''
import logging
from flask import Blueprint
from flask.globals import request
from son.editor.app.constants import get_parent
from son.editor.app.util import prepareResponse
from . import servicesimpl
from son.editor.app.util import getJSON

logger = logging.getLogger(__name__)

services_api = Blueprint("services_api", __name__)  # , url_prefix='/workspaces/<wsID>/projects'


@services_api.route('/<parentID>/services/', methods=['GET'])
def get_services(wsID, parentID):
    try:
        service = servicesimpl.get_services(wsID, parentID)
        return prepareResponse(service), 200
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 403
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 409


@services_api.route('/<parentID>/services/', methods=['POST'])
def create_service(wsID, parentID):
    try:
        service = servicesimpl.create_service(wsID, parentID)
        return prepareResponse(service), 201
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 403
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 409


@services_api.route('/<parentID>/services/<serviceID>', methods=['PUT'])
def update_service(wsID, parentID, serviceID):
    try:
        service = servicesimpl.update_service(wsID, parentID, serviceID)
        return prepareResponse(service), 200
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 403
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 409


@services_api.route('/<parentID>/services/<serviceID>', methods=['DELETE'])
def delete_service(wsID, parentID, serviceID):
    try:
        service = servicesimpl.delete_service(serviceID)
        return prepareResponse(service), 200
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 403
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args[0]), 409
