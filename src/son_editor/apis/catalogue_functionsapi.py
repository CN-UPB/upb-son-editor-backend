'''
Created on 22.07.2016

@author: Jonas
'''
from flask.globals import request, session
from flask_restplus import Namespace, Model, fields
from flask_restplus import Resource
from werkzeug.utils import secure_filename

from son_editor.app.exceptions import InvalidArgument
from son_editor.impl import functionsimpl, catalogue_servicesimpl
from son_editor.impl.private_catalogue_impl import publish_private_nsfs
from son_editor.util.constants import get_parent, Category, WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, VNFS
from son_editor.util.requestutil import prepare_response, get_json

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + CATALOGUES + "/<int:catalogue_id>/" + VNFS,
                      description="Catalogue VNF Resources")

funct = namespace.model("VNF", {
    'name': fields.String(required=True, description='The VNF Name'),
    'vendor': fields.String(required=True, description='The VNF Vendor'),
    'version': fields.String(required=True, description='The VNF Version')

})

funct_nest = namespace.model("VNF", {
    "descriptor": fields.Nested(model=funct, description="The Complete VNF Descriptor"),
    'id': fields.String(required=True, description='The VNF UID')
})

id = namespace.model("VNF_UID", {
    'id': fields.String(required=True, description='The VNF UID')
})

funct_response = funct.inherit("FunctionResponse", funct, {
    "descriptor": fields.Nested(model=funct, description="The Complete VNF Descriptor"),
    "id": fields.Integer(description='The Project ID'),
    "project_id": fields.Integer(description='The parent project id'),
})


@namespace.route('/')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('catalogue_id', 'The Catalogue identifier')
class Functions(Resource):
    """Resource methods for all function descriptors of this directory"""

    @namespace.response(200, "OK", [funct_response])
    def get(self, ws_id, catalogue_id):
        """List all functions

        Lists all available functions in the given project or catalogue."""

        functions = catalogue_servicesimpl.get_all_in_catalogue(ws_id, catalogue_id, True)
        return prepare_response(functions)

    @namespace.expect(id)
    @namespace.response(201, "Created", funct_response)
    def post(self, ws_id, catalogue_id):
        """Creates a new function

        Creates a new function in the project or catalogue"""

        vnf_data = get_json(request)
        vnf_data = catalogue_servicesimpl.create_in_catalogue(catalogue_id, vnf_data['id'],
                                                              True)
        return prepare_response(vnf_data, 201)


@namespace.route('/<string:vnf_id>')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('catalogue_id', 'The Catalogue identifier')
@namespace.param('vnf_id', 'The VNF identifier')
class Function(Resource):
    """Resource methods for specific function descriptors"""

    @namespace.expect(funct_nest)
    @namespace.response(200, "Updated", funct_response)
    def put(self, ws_id, catalogue_id, vnf_id):
        """Updates a function

        Updates a function in the project or catalogue by its id"""

        vnf_data = get_json(request)
        vnf_data = catalogue_servicesimpl.update_service_catalogue(ws_id, catalogue_id, vnf_id, vnf_data, True)
        return prepare_response(vnf_data)

    @namespace.response(200, "Deleted", funct_response)
    def delete(self, ws_id, catalogue_id, vnf_id):
        """Deletes a  function

        Deletes a function in the project or catalogue by its id"""

        deleted = catalogue_servicesimpl.delete_service_catalogue(ws_id, catalogue_id, vnf_id, True)
        return prepare_response(deleted)

    @namespace.response(200, "OK", funct_response)
    @namespace.expect(id)
    def get(self, ws_id, catalogue_id, vnf_id):
        """Get a specific function

        Gets a specific function information by its id"""

        functions = catalogue_servicesimpl.get_in_catalogue(ws_id, catalogue_id, vnf_id, True)
        return prepare_response(functions)
