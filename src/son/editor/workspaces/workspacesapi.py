'''
Created on 18.07.2016

@author: Jonas
'''
from flask import Blueprint
from son.editor.app.constants import WORKSPACES

workspaces_api = Blueprint("workspaces_api", __name__, url_prefix='/' + WORKSPACES)


@workspaces_api.route('/', methods=['GET'])
def get_workspaces():
    return "here be work spaces"


@workspaces_api.route('/', methods=['POST'])
def create_workspace():
    return "create workspace and return new ID"

@workspaces_api.route('/<wsID>', methods=['GET'])
def get_workspace(wsID):
    return "get info for workspace " + wsID

@workspaces_api.route('/<wsID>', methods=['PUT'])
def update_workspace(wsID):
    return "updating workspace " + wsID


@workspaces_api.route('/<wsID>', methods=['DELETE'])
def delete_workspace(wsID):
    return "deleting workspace " + wsID
