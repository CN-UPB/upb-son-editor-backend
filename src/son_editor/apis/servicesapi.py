'''
Created on 22.07.2016

@author: Jonas
'''
import logging

from flask import request
from flask_restplus import Model, Resource, Namespace, fields

from son_editor.impl import platform_connector
from son_editor.impl import servicesimpl
from son_editor.util import publishutil
from son_editor.util.constants import WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, SERVICES, get_parent, Category
from son_editor.util.requestutil import prepare_response

logger = logging.getLogger(__name__)

proj_namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PROJECTS + "/<int:parent_id>/" + SERVICES,
                           description="Project Service Resources")

cata_namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + CATALOGUES + "/<int:parent_id>/" + SERVICES,
                           description="Catalogue Service Resources")
plat_namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PLATFORMS + "/<int:parent_id>/" + SERVICES,
                           description="Platform Service Resources")

serv = Model("Service", {
    'name': fields.String(required=True, description='The Service Name'),
    'vendor': fields.String(required=True, description='The Service Vendor'),
    'version': fields.String(required=True, description='The Service Version')

})

serv_response = serv.inherit("ServiceResponse", serv, {
    "descriptor": fields.Nested(model=serv, description="The Complete Service Descriptor"),
    "id": fields.Integer(description='The Project ID'),
    "project_id": fields.Integer(description='The parent workspace id'),
})

proj_namespace.add_model(serv.name, serv)
proj_namespace.add_model(serv_response.name, serv_response)


@proj_namespace.route('/')
@cata_namespace.route('/')
@plat_namespace.route('/')
@proj_namespace.param('ws_id', 'The Workspace identifier')
@cata_namespace.param('ws_id', 'The Workspace identifier')
@plat_namespace.param('ws_id', 'The Workspace identifier')
@proj_namespace.param('parent_id', 'The Project identifier')
@cata_namespace.param('parent_id', 'The Catalogue identifier')
@plat_namespace.param('parent_id', 'The Platform identifier')
@proj_namespace.response(200, "OK")
class Services(Resource):
    @proj_namespace.response(200, "OK", [serv_response])
    def get(self, ws_id, parent_id):
        service = servicesimpl.get_services(ws_id, parent_id)
        return prepare_response(service)

    @proj_namespace.expect(serv)
    @proj_namespace.response(201, "Created", serv_response)
    def post(self, ws_id, parent_id):
        parent = get_parent(request)
        if parent == Category.project:
            service = servicesimpl.create_service(ws_id, parent_id)
            return prepare_response(service, 201)
        elif parent == Category.platform:
            result = platform_connector.create_service_on_platform(ws_id, parent_id)
            return prepare_response(result, 201)


@proj_namespace.route('/<int:service_id>')
@cata_namespace.route('/<int:service_id>')
@plat_namespace.route('/<int:service_id>')
@proj_namespace.param('ws_id', 'The Workspace identifier')
@cata_namespace.param('ws_id', 'The Workspace identifier')
@plat_namespace.param('ws_id', 'The Workspace identifier')
@proj_namespace.param('service_id', 'The Service identifier')
@cata_namespace.param('service_id', 'The Service identifier')
@plat_namespace.param('service_id', 'The Service identifier')
@proj_namespace.param('parent_id', 'The Project identifier')
@cata_namespace.param('parent_id', 'The Catalogue identifier')
@plat_namespace.param('parent_id', 'The Platform identifier')
@proj_namespace.response(200, "OK")
class Service(Resource):
    @proj_namespace.expect(serv)
    @proj_namespace.response(200, "Updated", serv_response)
    def put(self, ws_id, parent_id, service_id):
        service = servicesimpl.update_service(ws_id, parent_id, service_id)
        return prepare_response(service)

    @proj_namespace.response(200, "Deleted", serv_response)
    def delete(self, ws_id, parent_id, service_id):
        service = servicesimpl.delete_service(parent_id, service_id)
        return prepare_response(service)

    @proj_namespace.response(200, "OK", serv_response)
    def get(self, ws_id, parent_id, service_id):
        service = servicesimpl.get_service(ws_id, parent_id, service_id)
        return prepare_response(service)
