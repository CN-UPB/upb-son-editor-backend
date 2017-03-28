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

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PROJECTS + "/<int:project_id>/" + VNFS,
                      description="Project VNF Resources")

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

message_response = namespace.model("Message", {
    'message': fields.String(required=True, description="The result message")
})

namespace.add_model(funct.name, funct)
namespace.add_model(funct_response.name, funct_response)


@namespace.route('/')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('project_id', 'The Project identifier')
class Functions(Resource):
    """Resource methods for all function descriptors of this directory"""

    @namespace.response(200, "OK", [funct_response])
    def get(self, ws_id, project_id):
        """List all functions

        Lists all available functions in the given project or catalogue."""
        functions = functionsimpl.get_functions(ws_id, project_id)
        return prepare_response(functions)

    @namespace.expect(funct)
    @namespace.response(201, "Created", funct_response)
    def post(self, ws_id, project_id):
        """Creates a new function

        Creates a new function in the project or catalogue"""
        vnf_data = get_json(request)
        vnf_data = functionsimpl.create_function(ws_id, project_id, vnf_data)
        return prepare_response(vnf_data, 201)


@namespace.route('/<int:vnf_id>')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('parent_id', 'The Project identifier')
@namespace.param('vnf_id', 'The VNF identifier')
class Function(Resource):
    """Resource methods for specific function descriptors"""

    @namespace.expect(funct)
    @namespace.response(200, "Updated", funct_response)
    def put(self, ws_id, project_id, vnf_id):
        """Updates a function

        Updates a function in the project or catalogue by its id"""
        vnf_data = get_json(request)
        vnf_data = functionsimpl.update_function(ws_id, project_id, vnf_id, vnf_data)
        return prepare_response(vnf_data)

    @namespace.response(200, "Deleted", funct_response)
    def delete(self, ws_id, project_id, vnf_id):
        """Deletes a  function

        Deletes a function in the project or catalogue by its id"""
        deleted = functionsimpl.delete_function(ws_id, project_id, vnf_id)
        return prepare_response(deleted)

    @namespace.response(200, "OK", funct_response)
    def get(self, ws_id, project_id, vnf_id):
        """Get a specific function

        Gets a specific function information by its id"""
        functions = functionsimpl.get_function_project(ws_id, project_id, vnf_id)
        return prepare_response(functions)


@namespace.route('/<int:vnf_id>/upload')
class FunctionUpload(Resource):
    """ VNF Image upload"""
    @staticmethod
    def post(ws_id, project_id, vnf_id):
        """
        Upload a VNF image file
        
        Will accept a file attachment and save it into the VNF folder
        
        :param ws_id: The Workspace ID
        :param project_id: The Project ID
        :param vnf_id: The VNF ID
        :return: 
        """
        if 'image' not in request.files:
            raise InvalidArgument("No file attached!")
        file = request.files['image']
        return prepare_response(functionsimpl.save_image_file(ws_id, project_id, vnf_id, file))

    @staticmethod
    def get(ws_id, project_id, vnf_id):
        """
        List VNF Images
        
        Shows a list of all image files in the VNF Folder
        :param ws_id: The workspace ID
        :param project_id: The Project ID
        :param vnf_id: The VNF ID
        :return: A List of file names
        """
        return prepare_response(functionsimpl.get_image_files(ws_id, project_id, vnf_id))


@namespace.route('/<int:vnf_id>/upload/<filename>')
class FunctionUpload(Resource):

    @staticmethod
    def delete(ws_id, project_id, vnf_id, filename):
        """
        Delete VNF Image
        
        Delete the VNF Image by file name
        
        :param ws_id: The workspace ID
        :param project_id: The project ID
        :param vnf_id: The VNF ID
        :param filename: The filename to delete
        :return: 
        """
        return prepare_response(functionsimpl.delete_image_file(ws_id, project_id, vnf_id, filename))


@namespace.route('/<int:vnf_id>/publish')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('project_id', 'The Project identifier')
@namespace.param('vnf_id', 'The VNF identifier')
class PrivateService(Resource):
    @namespace.response(200, "OK", message_response)
    def get(self, ws_id, project_id, vnf_id):
        """
        Publish function to private

        Publishes the function to the workspace wide catalogue

        :param ws_id:
        :param project_id:
        :param vnf_id:
        :return:
        """
        function = functionsimpl.get_function_project(ws_id, project_id, vnf_id)
        publish_private_nsfs(ws_id, function["descriptor"], True)
        return prepare_response(
            {"message": "Function {} was published to private catalogue".format(function['descriptor']['name'])},
            201)
