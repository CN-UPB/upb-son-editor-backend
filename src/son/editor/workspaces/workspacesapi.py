'''
Created on 18.07.2016

@author: Jonas
'''
import logging

from flask import session
from flask.globals import request
from flask_restplus import Resource, Namespace
from flask_restplus import fields

from son.editor.app.constants import WORKSPACES
from son.editor.app.util import prepare_response, get_json
from . import workspaceimpl

namespace = Namespace(WORKSPACES, description="Workspace Resources")
logger = logging.getLogger("son-editor.workspacesapi")

ws = namespace.model("Workspace", {
    'name': fields.String(required=True, description='The Workspace Name')
})

ws_response = namespace.inherit("WorkspaceResponse", ws, {
    "path": fields.String(description='The Physical Workspace location'),
    "id": fields.Integer(description='The Workspace ID'),
    "owner_id": fields.Integer(description='The Workspaces Owner ID')
})


@namespace.route('/')
class Workspaces(Resource):
    @namespace.doc("list_workspaces")
    @namespace.response(200, "OK", [ws_response])
    def get(self):
        workspaces = workspaceimpl.get_workspaces(session['userData'])
        return prepare_response(workspaces)

    @namespace.doc("create_workspace")
    @namespace.expect(ws)
    @namespace.response(201, "Created", ws_response)
    @namespace.response(409, "Workspace already exists")
    def post(self):
        workspaceData = get_json(request)
        workspace = workspaceimpl.create_workspace(session['userData'], workspaceData)
        return prepare_response(workspace, 201)


@namespace.route('/<int:ws_id>')
@namespace.param("ws_id", "The workpace ID")
class Workspace(Resource):
    @namespace.doc("get_workspace")
    @namespace.response(200, "Ok", ws_response)
    @namespace.response(404, "Workspace not found")
    def get(self, ws_id):
        workspace = workspaceimpl.get_workspace(session['userData'], ws_id)
        return prepare_response(workspace)

    @namespace.doc("update_namespace")
    @namespace.expect(ws)
    @namespace.response(200, "Updated", ws_response)
    @namespace.response(404, "Workspace not found")
    @namespace.response(409, "Workspace already exists")
    def put(self, ws_id):
        workspaceData = get_json(request)
        workspace = workspaceimpl.update_workspace(workspaceData, ws_id)
        return prepare_response(workspace)

    @namespace.doc("delete_namespace")
    @namespace.response(200, "Deleted", ws_response)
    @namespace.response(404, "Workspace not found")
    def delete(self, ws_id):
        workspace = workspaceimpl.delete_workspace(ws_id)
        return prepare_response(workspace)
