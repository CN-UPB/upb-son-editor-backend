'''
Created on 22.07.2016

@author: Jonas
'''
from flask import Blueprint
from flask.globals import request
from son.editor.app.constants import get_parent

vnfs_api = Blueprint("vnfs_api", __name__)

@vnfs_api.route('/<parentID>/vnfs', methods=['GET'])

def get_vnfs(wsID, parentID):
    return "list of vnfs in this " + str(get_parent(request))


@vnfs_api.route('/<parentID>/vnfs', methods=['POST'])
def create_vnf(wsID, parentID):
    return "publish new vnf in project"


@vnfs_api.route('/<parentID>/vnfs/<vnfID>', methods=['PUT'])
def update_vnf(wsID, parentID, vnfID):
    return "update vnf in project with id " + parentID


@vnfs_api.route('/<parentID>/vnfs/<vnfID>', methods=['DELETE'])
def delete_vnf(wsID, parentID, vnfID):
    return "deleted vnf from project with id " + parentID
