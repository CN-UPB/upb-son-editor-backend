'''
Created on 22.07.2016

@author: Jonas
'''
import logging

from flask_restplus import Model, Resource, Namespace, fields

from son.editor.app.constants import WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, SERVICES
from son.editor.app.util import prepareResponse
from . import servicesimpl

logger = logging.getLogger(__name__)

proj_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PROJECTS + "/<int:parentID>/" + SERVICES,
                           description="Project Service Resources")

cata_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + CATALOGUES + "/<int:parentID>/" + SERVICES,
                           description="Catalogue Service Resources")
plat_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PLATFORMS + "/<int:parentID>/" + SERVICES,
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
@proj_namespace.response(200, "OK")
class Services(Resource):
    @proj_namespace.response(200, "OK", [serv_response])
    def get(self, wsID, parentID):
        service = servicesimpl.get_services(wsID, parentID)
        return prepareResponse(service)

    @proj_namespace.expect(serv)
    @proj_namespace.response(201, "Created", serv_response)
    def post(self, wsID, parentID):
        service = servicesimpl.create_service(wsID, parentID)
        return prepareResponse(service, 201)


@proj_namespace.route('/<int:serviceID>')
@cata_namespace.route('/<int:serviceID>')
@plat_namespace.route('/<int:serviceID>')
@proj_namespace.param('serviceID', 'The Service identifier')
@cata_namespace.param('serviceID', 'The Service identifier')
@plat_namespace.param('serviceID', 'The Service identifier')
@proj_namespace.response(200, "OK")
class Service(Resource):
    def put(self, wsID, parentID, serviceID):
        service = servicesimpl.update_service(wsID, parentID, serviceID)
        return prepareResponse(service)

    def delete(self, wsID, parentID, serviceID):
        service = servicesimpl.delete_service(parentID, serviceID)
        return prepareResponse(service)

    def get(self, wsID, parentID, serviceID):
        service = servicesimpl.get(wsID, parentID, serviceID)
        return prepareResponse(service)
