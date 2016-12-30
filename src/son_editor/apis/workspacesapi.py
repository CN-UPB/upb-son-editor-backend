""""
Created on 18.07.2016

@author: Jonas
"""
import logging

from flask import session
from flask.globals import request
from flask_restplus import Resource, Namespace
from flask_restplus import fields

from son_editor.impl import workspaceimpl
from son_editor.impl.private_catalogue_impl import get_private_nsfs_list
from son_editor.util.constants import WORKSPACES, SERVICES, VNFS
from son_editor.util.requestutil import prepare_response, get_json

namespace = Namespace(WORKSPACES, description="Workspace Resources")
logger = logging.getLogger(__name__)

rep = namespace.model("Repository", {
    'name': fields.String(required=True, description='The Repository Name'),
    'url': fields.Url(required=True, description='The Repository URL')
})

ws = namespace.model("Workspace", {
    'name': fields.String(required=True, description='The Workspace Name'),
    "catalogues": fields.List(fields.Nested(rep)),
    "platforms": fields.List(fields.Nested(rep))
})

ws_response = namespace.inherit("WorkspaceResponse", ws, {
    "path": fields.String(description='The Physical Workspace location'),
    "id": fields.Integer(description='The Workspace ID')
})

descriptor_content = namespace.model("Descriptor Content", {})

descriptor = namespace.model("Descriptor", {
    "id": fields.Integer(description="The descriptor id"),
    "descriptor": fields.Nested(descriptor_content)
})


@namespace.route('/')
class Workspaces(Resource):
    """Methods for the workspace resource directory"""

    @namespace.response(200, "OK", [ws_response])
    def get(self):
        """List workspaces

        Gets all available workspaces"""
        workspaces = workspaceimpl.get_workspaces(session['user_data']['login'])
        return prepare_response(workspaces)

    @namespace.expect(ws)
    @namespace.response(201, "Created", ws_response)
    @namespace.response(409, "Workspace already exists")
    def post(self):
        """Create workspace

        Creates a new workspace"""
        workspace_data = get_json(request)
        workspace = workspaceimpl.create_workspace(session['user_data']['login'], workspace_data)
        return prepare_response(workspace, 201)


@namespace.route('/<int:ws_id>')
@namespace.param("ws_id", "The workpace ID")
class Workspace(Resource):
    """Methods for a single workspace resource"""

    @namespace.response(200, "Ok", ws_response)
    @namespace.response(404, "Workspace not found")
    def get(self, ws_id):
        """Get workspace

        Gets information about a specific workspace"""
        workspace = workspaceimpl.get_workspace(ws_id)
        return prepare_response(workspace)

    @namespace.expect(ws)
    @namespace.response(200, "Updated", ws_response)
    @namespace.response(404, "Workspace not found")
    @namespace.response(409, "Workspace already exists")
    def put(self, ws_id):
        """Update workspace
        Updates a specific workspace by its id"""
        workspace_data = get_json(request)
        workspace = workspaceimpl.update_workspace(workspace_data, ws_id)
        return prepare_response(workspace)

    @namespace.response(200, "Deleted", ws_response)
    @namespace.response(404, "Workspace not found")
    def delete(self, ws_id):
        """Delete workspace

        Deletes a specific workspace by its id"""
        workspace = workspaceimpl.delete_workspace(ws_id)
        return prepare_response(workspace)


@namespace.route('/<int:ws_id>/' + SERVICES)
@namespace.param("ws_id", "The workpace ID")
class PrivateServices(Resource):
    """
    List Services of private Catalogue
    """

    @namespace.response(200, "Ok", [descriptor])
    def get(self, ws_id):
        """
        List private Catalogue services

        Lists all services in the Private workspace wide catalogue
        :param ws_id:
        :return:
        """
        return prepare_response(get_private_nsfs_list(ws_id, False))


@namespace.route('/<int:ws_id>/' + VNFS)
@namespace.param("ws_id", "The workspace ID")
class PrivateFunctions(Resource):
    """
    List functions of private Catalogue
    """

    @namespace.response(200, "Ok", [descriptor])
    def get(self, ws_id):
        """
        List private Catalogue functions

        Lists all functions in the Private workspace wide catalogue
        :param ws_id:
        :return:
        """
        return prepare_response(get_private_nsfs_list(ws_id, True))
