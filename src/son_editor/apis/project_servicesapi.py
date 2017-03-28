'''
Created on 22.07.2016

@author: Jonas
'''
import logging

from flask import request
from flask_restplus import Model, Resource, Namespace, fields

from son_editor.impl import servicesimpl
from son_editor.impl.private_catalogue_impl import publish_private_nsfs
from son_editor.util.constants import WORKSPACES, PROJECTS, SERVICES
from son_editor.util.requestutil import prepare_response, get_json

logger = logging.getLogger(__name__)

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PROJECTS + "/<int:project_id>/" + SERVICES,
                      description="Project Service Resources")
serv = Model("Service", {
    'name': fields.String(required=True, description='The Service Name'),
    'vendor': fields.String(required=True, description='The Service Vendor'),
    'version': fields.String(required=True, description='The Service Version')

})

serv_update = Model("Service Update", {
    "descriptor": fields.Nested(model=serv, description="The Complete Service Descriptor")

})

serv_response = serv.inherit("ServiceResponse", serv, {
    "descriptor": fields.Nested(model=serv, description="The Complete Service Descriptor"),
    "id": fields.Integer(description='The Project ID'),
    "project_id": fields.Integer(description='The parent workspace id'),
})

message_response = namespace.model("Message", {
    'message': fields.String(required=True, description="The result message")
})

namespace.add_model(serv_update.name, serv_update)
namespace.add_model(serv.name, serv)
namespace.add_model(serv_response.name, serv_response)


@namespace.route('/')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('project_id', 'The Project identifier')
@namespace.response(200, "OK")
class Services(Resource):
    """
    Api Methods for all services in this resource
    """

    @namespace.doc("Gets a list of services")
    @namespace.response(200, "OK", [serv_response])
    def get(self, ws_id, project_id):
        """Get a list of all Services
        Returns a list of all services available in this resource"""
        service = servicesimpl.get_services(ws_id, project_id)
        return prepare_response(service)

    @namespace.doc("Creates a new service in the project/platform or catalogue")
    @namespace.expect(serv)
    @namespace.response(201, "Created", serv_response)
    def post(self, ws_id, project_id):
        """Create a new Service

        Creates a new Service in this project or
        publishes it in the catalogue or platform"""
        service = servicesimpl.create_service(ws_id, project_id, get_json(request))
        return prepare_response(service, 201)


@namespace.route('/<int:service_id>')
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('service_id', 'The Service identifier')
@namespace.param('project_id', 'The Project identifier')
@namespace.response(200, "OK")
class Service(Resource):
    @namespace.expect(serv_update)
    @namespace.response(200, "Updated", serv_response)
    @namespace.doc("Updates the given service in the project/catalogue or platform")
    def put(self, ws_id, project_id, service_id):
        """Update the service

        Updates the referenced service in the project or in the catalogue or platform"""
        service = servicesimpl.update_service(ws_id, project_id, service_id, get_json(request))
        return prepare_response(service)

    @namespace.doc("Deletes a specific service by its id")
    @namespace.response(200, "Deleted", serv_response)
    def delete(self, ws_id, project_id, service_id):
        """Delete the Service

        Deletes the service from the Project or Catalogue"""
        service = servicesimpl.delete_service(project_id, service_id)
        return prepare_response(service)

    @namespace.response(200, "OK", serv_response)
    @namespace.doc("Returns a specific service by its id")
    def get(self, ws_id, project_id, service_id):
        """Return a specific Service

        Returns the referenced service from the Project or catalogue"""
        service = servicesimpl.get_service(ws_id, project_id, service_id)
        return prepare_response(service)


@namespace.route('/<int:service_id>/publish')
class PrivateService(Resource):
    """Private service publishing method"""

    @namespace.response(201, "OK", message_response)
    def get(self, ws_id, project_id, service_id):
        """
        Publish service to private

        Publishes the service to the workspace wide catalogue

        :param ws_id: The Workspace ID
        :param project_id: The Project ID
        :param service_id: The Service ID 
        :return: A dict with a "message" property.
        """
        service = servicesimpl.get_service(ws_id, project_id, service_id)
        publish_private_nsfs(ws_id, service["descriptor"], False)
        return prepare_response({"message": "Service {} was published to private catalogue".format(service.name)}, 201)
