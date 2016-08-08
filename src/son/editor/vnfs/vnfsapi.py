'''
Created on 22.07.2016

@author: Jonas
'''
from flask import Blueprint
from flask.globals import request
from son.editor.app.constants import get_parent
from son.editor.app.util import prepareResponse, getJSON

vnfs_api = Blueprint("vnfs_api", __name__)

@vnfs_api.route('/<parentID>/functions/', methods=['GET'])

def get_vnfs(wsID, parentID):
    #TODO actual implementation
    functions = {"functions": [{"name": "vnf1","id":1, "description":"blalalblaald"}]}
    return prepareResponse(functions)


@vnfs_api.route('/<parentID>/functions/', methods=['POST'])
def create_vnf(wsID, parentID):
    #TODO actual implementation
    vnfData = getJSON(request)
    vnfData["id"] = 2
    return prepareResponse(vnfData)


@vnfs_api.route('/<parentID>/functions/<vnfID>', methods=['PUT'])
def update_vnf(wsID, parentID, vnfID):
    return "update vnf in project with id " + parentID


@vnfs_api.route('/<parentID>/functions/<vnfID>', methods=['DELETE'])
def delete_vnf(wsID, parentID, vnfID):
    return "deleted vnf from project with id " + parentID
