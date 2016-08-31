'''
Created on 18.07.2016

@author: Jonas
'''
import logging

from flask import request, session
from flask_restplus import Namespace
from flask_restplus import Resource
from flask_restplus import fields

from son.editor.app.constants import WORKSPACES, PROJECTS
from son.editor.app.util import prepareResponse, getJSON
from . import projectsimpl

namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PROJECTS, description="Project Resources")
logger = logging.getLogger("son-editor.projectsapi")

pj = namespace.model("Project", {
    'name': fields.String(required=True, description='The Project Name')
})

pj_response = namespace.inherit("ProjectResponse", pj, {
    "rel_path": fields.String(description='The Projects location relative to its workpace'),
    "id": fields.Integer(description='The Project ID'),
    "workspace_id": fields.Integer(description='The parent workspace id')
})


@namespace.route('/')
class Projects(Resource):
    @namespace.doc("list_projects")
    @namespace.response(200, "OK", [pj_response])
    def get(self, wsID):
        projects = projectsimpl.get_projects(session['userData'], wsID)
        return prepareResponse(projects)

    @namespace.doc("create_project")
    @namespace.expect(pj)
    @namespace.response(201, "Created", pj_response)
    @namespace.response(409, "Project already exists")
    def post(self, wsID):
        projectData = getJSON(request)
        pj = projectsimpl.create_project(session['userData'], wsID, projectData)
        return prepareResponse(pj, 201)


@namespace.route('/<int:project_id>')
@namespace.param("wsID", "The workpace ID")
@namespace.param("project_id", "The project ID")
class Project(Resource):
    @namespace.doc("update_project")
    @namespace.expect(pj)
    @namespace.response(200, "Updated", pj_response)
    @namespace.response(404, "Project not found")
    @namespace.response(409, "Project already exists")
    def put(self, wsID, project_id):
        project_data = getJSON(request)
        return prepareResponse(projectsimpl.update_project(project_data, project_id))

    def delete(self, wsID, project_id):
        return prepareResponse(projectsimpl.delete_project(project_id))

    @namespace.doc("get_project")
    @namespace.response(200, "Ok", pj_response)
    @namespace.response(404, "Workspace not found")
    def get(self, wsID, project_id):
        return prepareResponse(projectsimpl.get_project(session['userData'], wsID, project_id))
