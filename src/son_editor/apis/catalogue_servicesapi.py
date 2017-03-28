'''
Created on 22.07.2016

@author: Jonas
'''
import logging

from flask import request
from flask_restplus import Model, Resource, Namespace, fields

from son_editor.impl import platform_connector
from son_editor.impl import servicesimpl, catalogue_servicesimpl
from son_editor.impl.private_catalogue_impl import publish_private_nsfs
from son_editor.util.constants import get_parent, Category, WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, SERVICES
from son_editor.util.requestutil import prepare_response, get_json

logger = logging.getLogger(__name__)

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + CATALOGUES + "/<int:catalogue_id>/" + SERVICES,
                      description="Catalogue Service Resources")


serv = namespace.model("Service", {
    'name': fields.String(required=True, description='The Service Name'),
    'vendor': fields.String(required=True, description='The Service Vendor'),
    'version': fields.String(required=True, description='The Service Version')

})

serv_update = namespace.model("Service Update", {
    "descriptor": fields.Nested(model=serv, description="The Complete Service Descriptor")

})

serv_id = namespace.model("Service ID", {
    'id': fields.Integer(required=True, description='The son-editor id of the service being published')
})

serv_response = namespace.inherit("ServiceResponse", serv, {
    "descriptor": fields.Nested(model=serv, description="The Complete Service Descriptor"),
    "id": fields.Integer(description='The Project ID'),
    "project_id": fields.Integer(description='The parent workspace id'),
})

message_response = namespace.model("Message", {
    'message': fields.String(required=True, description="The result message")
})


@namespace.route('/')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('catalogue_id', 'The Catalogue identifier')
class Services(Resource):
    """
    Api Methods for all services in this resource
    """

    @namespace.doc("Gets a list of services")
    @namespace.response(200, "OK", [serv_response])
    def get(self, ws_id, catalogue_id):
        """Get a list of all Services
        Returns a list of all services available in this resource"""

        service = catalogue_servicesimpl.get_all_in_catalogue(ws_id, catalogue_id, False)
        return prepare_response(service)

    @namespace.doc("Creates a new service in the project/platform or catalogue")
    @namespace.expect(serv)
    @namespace.expect(serv_id)
    @namespace.response(201, "Created", serv_response)
    @namespace.response(201, "Created")
    def post(self, ws_id, catalogue_id):
        """Create a new Service

        Creates a new Service in this project or
        publishes it in the catalogue or platform"""

        vnf_data = get_json(request)
        service = catalogue_servicesimpl.create_in_catalogue(catalogue_id, vnf_data['id'], False)
        return prepare_response(service)


@namespace.route('/<string:service_id>')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('service_id', 'The Service identifier')
@namespace.param('catalogue_id', 'The Catalogue identifier')
class Service(Resource):
    @namespace.expect(serv_update)
    @namespace.expect(serv_id)
    @namespace.response(200, "Updated", serv_response)
    @namespace.doc("Updates the given service in the project/catalogue or platform")
    def put(self, ws_id, catalogue_id, service_id):
        """Update the service

        Updates the referenced service in the project or in the catalogue or platform"""

        function_data = get_json(request)
        service = catalogue_servicesimpl.update_service_catalogue(ws_id, catalogue_id, service_id, function_data,
                                                                  False)
        return prepare_response(service)

    @namespace.doc("Deletes a specific service by its id")
    @namespace.response(200, "Deleted", serv_response)
    def delete(self, ws_id, catalogue_id, service_id):
        """Delete the Service

        Deletes the service from the Project or Catalogue"""

        service = catalogue_servicesimpl.delete_service_catalogue(ws_id, catalogue_id, service_id, False)
        return prepare_response(service)

    @namespace.response(200, "OK", serv_response)
    @namespace.doc("Returns a specific service by its id")
    def get(self, ws_id, catalogue_id, service_id):
        """Return a specific Service

        Returns the referenced service from the Project or catalogue"""

        service = catalogue_servicesimpl.get_in_catalogue(ws_id, catalogue_id, service_id, False)
        return prepare_response(service)