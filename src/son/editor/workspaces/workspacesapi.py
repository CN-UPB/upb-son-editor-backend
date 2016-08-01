'''
Created on 18.07.2016

@author: Jonas
'''
import json

from flask import Blueprint, session
from flask.globals import request

from son.editor.app import util
from son.editor.app.constants import WORKSPACES
from . import workspaceimpl


workspaces_api = Blueprint("workspaces_api", __name__, url_prefix='/' + WORKSPACES)

@workspaces_api.route('/', methods=['GET'])
def get_workspaces():
    workspaces = workspaceimpl.get_workspaces(session['userData']['login'])
    return util.prepareResponse({"workspaces":workspaces})

@workspaces_api.route('/', methods=['POST'])
def create_workspace():
    if request.content_type == "application/json":
        workspaceData = request.get_json()
    if workspaceData == None:
        workspaceData = json.loads(request.get_data().decode("utf8"))
    print(request.get_data())
    try:
        ws = workspaceimpl.create_workspace(session['userData']['login'], workspaceData)
        return util.prepareResponse(json.dumps(ws))
    except Exception as err:
        return err.args[0], 409

@workspaces_api.route('/<wsID>', methods=['GET'])
def get_workspace(wsID):
    return "get info for workspace " + wsID

@workspaces_api.route('/<wsID>', methods=['PUT'])
def update_workspace(wsID):
    return "updating workspace " + wsID


@workspaces_api.route('/<wsID>', methods=['DELETE'])
def delete_workspace(wsID):
    return "deleting workspace " + wsID

