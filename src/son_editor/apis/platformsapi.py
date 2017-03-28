"""
Created on 18.07.2016

@author: Jonas
"""
from flask_restplus import Resource, Namespace, Model, fields
from flask.globals import request
from son_editor.util.requestutil import get_json
from son_editor.impl import platformsimpl, platform_connector
from son_editor.util.constants import WORKSPACES, PLATFORMS, SERVICES
from son_editor.util.requestutil import prepare_response

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PLATFORMS, description="Platform Resources")

serv_id = Model("Service ID", {
    'id': fields.Integer(required=True, description='The son-editor id of the service being published')
})

namespace.add_model(serv_id.name, serv_id)


@namespace.route("/")
@namespace.response(200, "OK")
class Platforms(Resource):
    """Platforms"""

    def get(self, ws_id):
        """List platforms

        Lists all service platforms in the given workspace"""
        return prepare_response(platformsimpl.get_platforms(ws_id))

    @namespace.doc("")
    def post(self, ws_id):
        """Create a new service platform

        Creates a new service platform in the given workspace"""
        return prepare_response(platformsimpl.create_platform(ws_id, get_json(request)), 201)


@namespace.route("/<int:platform_id>")
@namespace.param('platform_id', 'The Platform identifier')
@namespace.response(200, "OK")
class Platform(Resource):
    def get(self, ws_id, platform_id):
        """Get service Platform
        
        Retrieves a service platform by its id"""
        return prepare_response(platformsimpl.get_platform(platform_id))

    def put(self, ws_id, platform_id):
        """Update platform
        
        Updates a service platform by its id"""
        return prepare_response(platformsimpl.update_platform(ws_id, platform_id, get_json(request)))

    def delete(self, ws_id, platform_id):
        """Delete Platform
        
        Deletes a service platform by its id"""
        return prepare_response(platformsimpl.delete(ws_id, platform_id))


@namespace.route("/<int:platform_id>/"+SERVICES+"/")
@namespace.param('platform_id', 'The Platform identifier')
@namespace.response(200, "OK")
class PlatformServices(Resource):

    @namespace.expect(serv_id)
    def post(self, ws_id, platform_id):
        """
        Upload a service package
        
        Packages and uploads a network service to the platform
        """
        result = platform_connector.create_service_on_platform(ws_id, platform_id, get_json(request))
        return prepare_response(result, 201)
