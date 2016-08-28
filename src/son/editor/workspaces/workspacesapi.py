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
    workspaces = workspaceimpl.get_workspaces(session['userData'])
    return prepareResponse(workspaces)


@workspaces_api.route('/', methods=['POST'])
def create_workspace():
    workspaceData = getJSON(request)
    ws = workspaceimpl.create_workspace(session['userData'], workspaceData)
    return prepareResponse(ws), 201


@workspaces_api.route('/<wsID>', methods=['GET'])
def get_workspace(wsID):
    workspace = workspaceimpl.get_workspace(session['userData'], wsID)
    return prepareResponse(workspace)


@workspaces_api.route('/<wsID>', methods=['PUT'])
def update_workspace(wsID):
    workspaceData = getJSON(request)
    workspace = workspaceimpl.update_workspace(workspaceData, wsID)
    return prepareResponse(workspace)


@workspaces_api.route('/<wsID>', methods=['DELETE'])
def delete_workspace(wsID):
    workspace = workspaceimpl.delete_workspace(wsID)
    return prepareResponse(workspace)
