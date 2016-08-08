'''
Created on 18.07.2016

@author: Jonas
'''
import json

from flask import Blueprint, Response
from flask import session

from son.editor.app.constants import WORKSPACES, PROJECTS
from son.editor.app.util import prepareResponse
from . import projectsimpl

projects_api = Blueprint("projects_api", __name__, url_prefix='/' + WORKSPACES + '/<wsID>/' + PROJECTS)


@projects_api.route('/', methods=['GET'])
def get_projects(wsID):
    projects = {"projects":projectsimpl.get_projects(session['userData'], wsID)}
    return prepareResponse(projects)


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
