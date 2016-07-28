'''
Created on 18.07.2016

@author: Jonas
'''
import json

from flask import Blueprint, Response

from son.editor.app.constants import WORKSPACES, PROJECTS


projects_api = Blueprint("projects_api", __name__, url_prefix='/' + WORKSPACES + '/<wsID>/' + PROJECTS)


@projects_api.route('/', methods=['GET'])
def get_projects(wsID):
    response = Response(json.dumps({"projects":[{"name":"project1", "id":"1234"}, {"name":"project2", "id":"4321"}]}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@projects_api.route('/', methods=['POST'])
def create_project(wsID):
    return "create new project and return id"


@projects_api.route('/<projectID>', methods=['PUT'])
def update_project(wsID, projectID):
    return "update project " + projectID + " in workspace " + wsID


@projects_api.route('/<projectID>', methods=['DELETE'])
def delete_project(wsID, projectID):
    return "delete project " + projectID + " in workspace " + wsID


@projects_api.route('/<projectID>', methods=['GET'])
def get_project(wsID, projectID):
    return "here be project " + projectID + " in workspace " + wsID
