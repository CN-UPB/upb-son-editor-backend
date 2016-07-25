'''
Created on 18.07.2016

@author: Jonas
'''
from flask import Blueprint
from son.editor.app.constants import WORKSPACES, CATALOGUES

catalogues_api = Blueprint("catalogues_api", __name__, url_prefix='/' + WORKSPACES + '/<wsID>/' + CATALOGUES)


@catalogues_api.route('/', methods=['GET'])
def get_catalogues(wsID):
    return "list of catalogues"


@catalogues_api.route('/', methods=['POST'])
def create_catalogue(wsID):
    return "create new catalogue and return id"


@catalogues_api.route('/<catalogueID>', methods=['PUT'])
def update_catalogue(wsID, catalogueID):
    return "update catalogue with id " + catalogueID


@catalogues_api.route('/<catalogueID>', methods=['DELETE'])
def delete_catalogue(wsID, catalogueID):
    return "deleted catalogue with id " + catalogueID
