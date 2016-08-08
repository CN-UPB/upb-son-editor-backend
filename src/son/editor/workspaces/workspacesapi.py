'''
Created on 18.07.2016

@author: Jonas
'''
import json

from flask import Blueprint, session
from flask.globals import request

from son.editor.app.constants import WORKSPACES
from son.editor.app.util import prepareResponse, getJSON

from . import workspaceimpl

workspaces_api = Blueprint("workspaces_api", __name__, url_prefix='/' + WORKSPACES)


@workspaces_api.route('/', methods=['GET'])
def get_workspaces():
    workspaces = workspaceimpl.get_workspaces(session['userData'])
    return prepareResponse({"workspaces": workspaces})


@workspaces_api.route('/', methods=['POST'])
def create_workspace():
    workspaceData = getJSON(request)
    try:
        ws = workspaceimpl.create_workspace(session['userData'], workspaceData)
        return prepareResponse(ws)
    except Exception as err:
        return prepareResponse(err.args[0]), 409


@workspaces_api.route('/<wsID>', methods=['GET'])
def get_workspace(wsID):
    try:
        workspace = workspaceimpl.get_workspace(session['userData'], wsID)
        return prepareResponse(workspace)
    except Exception as err:
        return prepareResponse(str_data=err.args[0]), 409


@workspaces_api.route('/<wsID>', methods=['PUT'])
def update_workspace(wsID):
    return "updating workspace " + wsID


@workspaces_api.route('/<wsID>', methods=['DELETE'])
def delete_workspace(wsID):
    return "deleting workspace " + wsID
