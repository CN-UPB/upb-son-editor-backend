'''
Created on 18.07.2016

@author: Jonas
'''
import logging

from flask import Blueprint, session
from flask.globals import request

from son.editor.app.constants import WORKSPACES
from son.editor.app.exceptions import NameConflict, NotFound
from son.editor.app.util import prepareResponse, getJSON
from . import workspaceimpl

workspaces_api = Blueprint("workspaces_api", __name__, url_prefix='/' + WORKSPACES)
logger = logging.getLogger("son-editor.workspacesapi")


@workspaces_api.route('/', methods=['GET'])
def get_workspaces():
    try:
        workspaces = workspaceimpl.get_workspaces(session['userData'])
        return prepareResponse(workspaces)
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 403
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 500


@workspaces_api.route('/', methods=['POST'])
def create_workspace():
    workspaceData = getJSON(request)
    try:
        ws = workspaceimpl.create_workspace(session['userData'], workspaceData)
        return prepareResponse(ws), 201
    except NameConflict as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 409
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 400
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 500


@workspaces_api.route('/<wsID>', methods=['GET'])
def get_workspace(wsID):
    try:
        workspace = workspaceimpl.get_workspace(session['userData'], wsID)
        return prepareResponse(workspace)
    except NotFound as err:
        logger.warn(err.msg)
        return prepareResponse(err.msg), 404
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 403
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 500


@workspaces_api.route('/<wsID>', methods=['PUT'])
def update_workspace(wsID):
    workspaceData = getJSON(request)
    try:
        workspace = workspaceimpl.update_workspace(workspaceData, wsID)
        return prepareResponse(workspace)
    except NameConflict as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 409
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 400
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 500


@workspaces_api.route('/<wsID>', methods=['DELETE'])
def delete_workspace(wsID):
    try:
        workspace = workspaceimpl.delete_workspace(wsID)
        return prepareResponse(workspace)
    except NameConflict as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 409
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 400
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 500
