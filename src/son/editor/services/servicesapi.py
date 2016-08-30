'''
Created on 22.07.2016

@author: Jonas
'''
import logging

from flask_restplus import Resource, Namespace

from son.editor.app.util import prepareResponse
from son.editor.app.constants import WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, SERVICES
from . import servicesimpl

logger = logging.getLogger(__name__)

proj_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PROJECTS + "/<int:parentID>/" + SERVICES,
                           description="Project Service Resources")


cata_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + CATALOGUES + "/<int:parentID>/" + SERVICES,
                           description="Catalogue Service Resources")
plat_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PLATFORMS + "/<int:parentID>/" + SERVICES,
                           description="Platform Service Resources")


@proj_namespace.route('/')
@cata_namespace.route('/')
@plat_namespace.route('/')
@proj_namespace.response(200, "OK")
class Services(Resource):
    def get(self, wsID, parentID):
        service = servicesimpl.get_services(wsID, parentID)
        return prepareResponse(service)

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
