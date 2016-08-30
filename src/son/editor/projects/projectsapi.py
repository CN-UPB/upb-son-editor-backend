'''
Created on 18.07.2016

@author: Jonas
'''
import logging

from flask import request, session
from flask_restplus import Namespace
from flask_restplus import Resource

from son.editor.app.constants import WORKSPACES, PROJECTS
from son.editor.app.exceptions import NotFound, NameConflict
from son.editor.app.util import prepareResponse, getJSON
from . import projectsimpl

namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PROJECTS, description="Project Resources")
logger = logging.getLogger("son-editor.projectsapi")


@namespace.route('/')
class Projects(Resource):
    def get(self, wsID):
        projects = projectsimpl.get_projects(session['userData'], wsID)
        return prepareResponse(projects)

    def post(self, wsID):
        projectData = getJSON(request)
        pj = projectsimpl.create_project(session['userData'], wsID, projectData)
        return prepareResponse(pj, 201)


@namespace.route('/<int:projectID>')
class Project(Resource):
    def put(self, wsID, projectID):
        return "update project " + projectID + " in workspace " + wsID + " (not really though)"

    def delete(self, wsID, projectID):
        return "deleting project " + projectID + " in workspace " + wsID + " (not really though)"

    def get(self, wsID, projectID):
        return prepareResponse(projectsimpl.get_project(session['userData'], wsID, projectID))