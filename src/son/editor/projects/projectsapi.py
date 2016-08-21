'''
Created on 18.07.2016

@author: Jonas
'''
import logging

from flask import Blueprint
from flask import request
from flask import session

from son.editor.app.constants import WORKSPACES, PROJECTS
from son.editor.app.exceptions import NotFound
from son.editor.app.util import prepareResponse, getJSON
from . import projectsimpl

projects_api = Blueprint("projects_api", __name__, url_prefix='/' + WORKSPACES + '/<wsID>/' + PROJECTS)
logger = logging.getLogger("son-editor.projectsapi")


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
    return "update project " + projectID + " in workspace " + wsID +" (not really though)"


@projects_api.route('/<projectID>', methods=['DELETE'])
def delete_project(wsID, projectID):
    return "deleting project " + projectID + " in workspace " + wsID +" (not really though)"


@projects_api.route('/<projectID>', methods=['GET'])
def get_project(wsID, projectID):
    try:
        return prepareResponse(projectsimpl.get_project(session['userData'], wsID,projectID))
    except NotFound as err:
        logger.warn(err.msg)
        return prepareResponse(err.msg), 404
    except KeyError as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 403
    except Exception as err:
        logger.exception(err.args[0])
        return prepareResponse(err.args), 500


