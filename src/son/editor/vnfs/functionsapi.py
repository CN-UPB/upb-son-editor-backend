'''
Created on 22.07.2016

@author: Jonas
'''
from flask.globals import request, session
from flask_restplus import Namespace, Model, fields
from flask_restplus import Resource

from son.editor.app.constants import get_parent, Category, WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, VNFS
from son.editor.app.util import prepare_response, get_json
from son.editor.vnfs import functionsimpl

proj_namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PROJECTS + "/<int:parent_id>/" + VNFS,
                           description="Project VNF Resources")
cata_namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + CATALOGUES + "/<int:parent_id>/" + VNFS,
                           description="Catalogue VNF Resources")
plat_namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PLATFORMS + "/<int:parent_id>/" + VNFS,
                           description="Platform VNF Resources")

funct = Model("VNF", {
    'name': fields.String(required=True, description='The VNF Name'),
    'vendor': fields.String(required=True, description='The VNF Vendor'),
    'version': fields.String(required=True, description='The VNF Version')

})

funct_response = funct.inherit("FunctionResponse", funct, {
    "descriptor": fields.Nested(model=funct, description="The Complete VNF Descriptor"),
    "id": fields.Integer(description='The Project ID'),
    "project_id": fields.Integer(description='The parent project id'),
})

proj_namespace.add_model(funct.name, funct)
proj_namespace.add_model(funct_response.name, funct_response)


@proj_namespace.route('/')
@cata_namespace.route('/')
@plat_namespace.route('/')
@proj_namespace.param('ws_id', 'The Workspace identifier')
@cata_namespace.param('ws_id', 'The Workspace identifier')
@plat_namespace.param('ws_id', 'The Workspace identifier')
@proj_namespace.param('parent_id', 'The Project identifier')
@cata_namespace.param('parent_id', 'The Catalogue identifier')
@plat_namespace.param('parent_id', 'The Platform identifier')
class Functions(Resource):
    @proj_namespace.response(200, "OK", [funct_response])
    def get(self, ws_id, parent_id):
        if get_parent(request) is Category.project:
            functions = functionsimpl.get_functions(session["userData"], ws_id, parent_id)
            return prepare_response(functions)
        return prepare_response("not yet implemented")

    @proj_namespace.expect(funct)
    @proj_namespace.response(201, "Created", funct_response)
    def post(self, ws_id, parent_id):
        if get_parent(request) is Category.project:
            vnf_data = get_json(request)
            vnf_data = functionsimpl.create_function(session['userData'], ws_id, parent_id, vnf_data)
            return prepare_response(vnf_data, 201)
        # TODO implement for catalog and platform
        return prepare_response("not implemented yet")


@proj_namespace.route('/<int:vnf_id>')
@cata_namespace.route('/<int:vnf_id>')
@plat_namespace.route('/<int:vnf_id>')
@proj_namespace.param('ws_id', 'The Workspace identifier')
@cata_namespace.param('ws_id', 'The Workspace identifier')
@plat_namespace.param('ws_id', 'The Workspace identifier')
@proj_namespace.param('parent_id', 'The Project identifier')
@cata_namespace.param('parent_id', 'The Catalogue identifier')
@plat_namespace.param('parent_id', 'The Platform identifier')
@proj_namespace.param('vnf_id', 'The VNF identifier')
@cata_namespace.param('vnf_id', 'The VNF identifier')
@plat_namespace.param('vnf_id', 'The VNF identifier')
class Function(Resource):
    @proj_namespace.expect(funct)
    @proj_namespace.response(200, "Updated", funct_response)
    def put(self, ws_id, parent_id, vnf_id):
        if get_parent(request) is Category.project:
            vnf_data = get_json(request)
            vnf_data = functionsimpl.update_function(session['userData'], ws_id, parent_id, vnf_id, vnf_data)
            return prepare_response(vnf_data)
        # TODO implement for catalog and platform
        return prepare_response("update vnf in project with id " + parent_id)

    @proj_namespace.response(200, "Deleted", funct_response)
    def delete(self, ws_id, parent_id, vnf_id):
        if get_parent(request) is Category.project:
            deleted = functionsimpl.delete_function(session['userData'], ws_id, parent_id, vnf_id)
            return prepare_response(deleted)
        # TODO implement for catalog and platform
        return prepare_response("not yet implemented")

    @proj_namespace.response(200, "OK", funct_response)
    def get(self, ws_id, parent_id, vnf_id):
        if get_parent(request) is Category.project:
            functions = functionsimpl.get_function(session["userData"], ws_id, parent_id, vnf_id)
            return prepare_response(functions)
        # TODO implement for catalog and platform
        return prepare_response("not yet implemented")
