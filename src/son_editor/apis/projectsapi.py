'''
Created on 18.07.2016

@author: Jonas
'''
import logging

from flask import request, session
from flask_restplus import Namespace
from flask_restplus import Resource
from flask_restplus import fields

from son_editor.impl import projectsimpl
from son_editor.util.constants import WORKSPACES, PROJECTS
from son_editor.util.requestutil import prepare_response, get_json

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PROJECTS, description="Project Resources")
logger = logging.getLogger(__name__)

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
    @namespace.response(200, "OK", [pj_response])
    def get(self, ws_id):
        """Lists projects

        Lists projects in the given workspace"""
        projects = projectsimpl.get_projects(ws_id)
        return prepare_response(projects)

    @namespace.expect(pj)
    @namespace.response(201, "Created", pj_response)
    @namespace.response(409, "Project already exists")
    def post(self, ws_id):
        """Creates a new project

        Creates a new project in the given workspace"""
        projectData = get_json(request)
        pj = projectsimpl.create_project(ws_id, projectData)
        return prepare_response(pj, 201)


@namespace.route('/<int:project_id>')
@namespace.param("ws_id", "The workpace ID")
@namespace.param("project_id", "The project ID")
class Project(Resource):
    @namespace.expect(pj)
    @namespace.response(200, "Updated", pj_response)
    @namespace.response(404, "Project not found")
    @namespace.response(409, "Project already exists")
    def put(self, ws_id, project_id):
        """Updates a project

        Updates the project by its id"""
        project_data = get_json(request)
        return prepare_response(projectsimpl.update_project(project_data, project_id))

    def delete(self, ws_id, project_id):
        """Delete project

        Deletes the project by its id"""
        return prepare_response(projectsimpl.delete_project(project_id))

    @namespace.response(200, "Ok", pj_response)
    @namespace.response(404, "Workspace not found")
    def get(self, ws_id, project_id):
        """Retrieves project

        Gets information of a given project"""
        return prepare_response(projectsimpl.get_project(ws_id, project_id))
