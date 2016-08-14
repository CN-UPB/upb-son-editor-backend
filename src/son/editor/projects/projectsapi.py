'''
Created on 18.07.2016

@author: Jonas
'''
import json

from flask import Blueprint
from flask import request
from flask import session

from son.editor.app.constants import WORKSPACES, PROJECTS
from son.editor.app.util import prepareResponse, getJSON
from . import projectsimpl

projects_api = Blueprint("projects_api", __name__, url_prefix='/' + WORKSPACES + '/<wsID>/' + PROJECTS)


@projects_api.route('/', methods=['GET'])
def get_projects(wsID):
    projects = {"projects":projectsimpl.get_projects(session['userData'], wsID)}
    return prepareResponse(projects)


@projects_api.route('/', methods=['POST'])
def create_project(wsID):
    projectData = getJSON(request)
    try:
        pj = projectsimpl.create_project(session['userData'],wsID, projectData)
        return prepareResponse(pj)
    except Exception as err:
        return prepareResponse(err.args[0]), 409


@projects_api.route('/<projectID>', methods=['PUT'])
def update_project(wsID, projectID):
    return "update project " + projectID + " in workspace " + wsID


@projects_api.route('/<projectID>', methods=['DELETE'])
def delete_project(wsID, projectID):
    return "delete project " + projectID + " in workspace " + wsID


@projects_api.route('/<projectID>', methods=['GET'])
def get_project(wsID, projectID):
    return "here be project " + projectID + " in workspace " + wsID
