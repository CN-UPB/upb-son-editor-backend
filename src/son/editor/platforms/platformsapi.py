'''
Created on 18.07.2016

@author: Jonas
'''
from flask import Blueprint
from son.editor.app.constants import WORKSPACES, PLATFORMS

platforms_api = Blueprint("platforms_api", __name__, url_prefix='/' + WORKSPACES + '/<wsID>/' + PLATFORMS)


@platforms_api.route('/', methods=['GET'])
def get_platforms(wsID):
    return "list of service platforms"


@platforms_api.route('/', methods=['POST'])
def create_platform(wsID):
    return "create new service platform and return id"


@platforms_api.route('/<platformID>', methods=['PUT'])
def update_platform(wsID, platformID):
    return "update platform with id " + platformID


@platforms_api.route('/<platformID>', methods=['DELETE'])
def delete_platform(wsID, platformID):
    return "deleted platform with id " + platformID
