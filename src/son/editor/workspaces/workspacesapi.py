'''
Created on 18.07.2016

@author: Jonas
'''
import json

from flask import Blueprint
from flask.globals import request

from son.editor.app import util
from son.editor.app.constants import WORKSPACES


workspaces_api = Blueprint("workspaces_api", __name__, url_prefix='/' + WORKSPACES)


@workspaces_api.route('/', methods=['GET'])
def get_workspaces():
    workspaces = {"workspaces":
        [
            {"name":"workspace1", "id":"1234"},
            {"name":"workspace2", "id":"4321"}
        ]
    }
    return util.prepareResponse(workspaces)

@workspaces_api.route('/', methods=['POST'])
def create_workspace():
    workspaceData = request.get_json()
    workspaceData['id'] = "4422"
    return json.dumps(workspaceData)

@workspaces_api.route('/<wsID>', methods=['GET'])
def get_workspace(wsID):
    return "get info for workspace " + wsID

@workspaces_api.route('/<wsID>', methods=['PUT'])
def update_workspace(wsID):
    return "updating workspace " + wsID


@workspaces_api.route('/<wsID>', methods=['DELETE'])
def delete_workspace(wsID):
    return "deleting workspace " + wsID

