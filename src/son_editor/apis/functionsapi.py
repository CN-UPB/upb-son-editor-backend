'''
Created on 22.07.2016

@author: Jonas
'''
from flask.globals import request, session
from flask_restplus import Namespace, Model, fields
from flask_restplus import Resource

from son_editor.impl import functionsimpl, catalogue_servicesimpl
from son_editor.util.constants import get_parent, Category, WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, VNFS
from son_editor.util.requestutil import prepare_response, get_json

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

funct_uid = Model("VNF", {
    'id': fields.String(required=True, description='The VNF UID'),
    'name': fields.String(required=True, description='The VNF Name'),
    'vendor': fields.String(required=True, description='The VNF Vendor'),
    'version': fields.String(required=True, description='The VNF Version')

})

uid = Model("VNF_UID", {
    'id': fields.String(required=True, description='The VNF UID')
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
    """Resource methods for all function descriptors of this directory"""

    @proj_namespace.response(200, "OK", [funct_response])
    def get(self, ws_id, parent_id):
        """List all functions

        Lists all available functions in the given project or catalogue."""
        if get_parent(request) is Category.project:
            functions = functionsimpl.get_functions(ws_id, parent_id)
            return prepare_response(functions)
        if get_parent(request) is Category.catalogue:
            functions = catalogue_servicesimpl.get_all_in_catalogue(ws_id, parent_id, True)
            return prepare_response(functions)
        return prepare_response("not yet implemented")

    @proj_namespace.expect(funct)
    @proj_namespace.response(201, "Created", funct_response)
    def post(self, ws_id, parent_id):
        """Creates a new function

        Creates a new function in the project or catalogue"""
        if get_parent(request) is Category.project:
            vnf_data = get_json(request)
            vnf_data = functionsimpl.create_function(ws_id, parent_id, vnf_data)
            return prepare_response(vnf_data, 201)
        if get_parent(request) is Category.catalogue:
            vnf_data = get_json(request)
            vnf_data = catalogue_servicesimpl.create_in_catalogue(parent_id, vnf_data['id'],
                                                                  True)
            return prepare_response(vnf_data, 201)
        # TODO implement for catalog and platform
        return prepare_response("not implemented yet")


@proj_namespace.route('/<int:vnf_id>')
@cata_namespace.route('/<string:vnf_id>')
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
    """Resource methods for specific function descriptors"""

    @proj_namespace.expect(funct)
    @cata_namespace.expect(funct_uid)
    @proj_namespace.response(200, "Updated", funct_response)
    def put(self, ws_id, parent_id, vnf_id):
        """Updates a function

        Updates a function in the project or catalogue by its id"""
        if get_parent(request) is Category.project:
            vnf_data = get_json(request)
            vnf_data = functionsimpl.update_function(ws_id, parent_id, vnf_id, vnf_data)
            return prepare_response(vnf_data)
        if get_parent(request) is Category.catalogue:
            vnf_data = get_json(request)
            vnf_data = catalogue_servicesimpl.update_service_catalogue(ws_id, parent_id, vnf_id, vnf_data, True)
            return prepare_response(vnf_data)
        return prepare_response("update vnf in project with id " + parent_id)

    @proj_namespace.response(200, "Deleted", funct_response)
    def delete(self, ws_id, parent_id, vnf_id):
        """Deletes a  function

        Deletes a function in the project or catalogue by its id"""
        if get_parent(request) is Category.project:
            deleted = functionsimpl.delete_function( ws_id, parent_id, vnf_id)
            return prepare_response(deleted)
        if get_parent(request) is Category.catalogue:
            deleted = catalogue_servicesimpl.delete_service_catalogue(ws_id, parent_id, vnf_id, True)
            return prepare_response(deleted)
        # TODO implement for catalog and platform
        return prepare_response("not yet implemented")

    @proj_namespace.response(200, "OK", funct_response)
    # @cata_namespace.expect(uid)
    def get(self, ws_id, parent_id, vnf_id):
        """Get a specific function

        Gets a specific function information by its id"""
        if get_parent(request) is Category.project:
            functions = functionsimpl.get_function_project(ws_id, parent_id, vnf_id)
            return prepare_response(functions)
            # TODO implement for catalog and platform
        if get_parent(request) is Category.catalogue:
            functions = catalogue_servicesimpl.get_in_catalogue(ws_id, parent_id, vnf_id, True)
            return prepare_response(functions)
        # TODO implement for catalog and platform
        return prepare_response("not yet implemented")
