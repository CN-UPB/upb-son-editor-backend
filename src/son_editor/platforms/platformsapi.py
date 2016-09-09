"""
Created on 18.07.2016

@author: Jonas
"""
from flask_restplus import Resource, Namespace

from son_editor.app.util import prepare_response
from son_editor.app.constants import WORKSPACES, PLATFORMS
from son_editor.platforms import platformsimpl

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PLATFORMS, description="Platform Resources")


@namespace.route("/")
@namespace.response(200, "OK")
class Platforms(Resource):
    "Platforms"

    @namespace.doc("list platforms")
    def get(self, ws_id):
        return prepare_response(platformsimpl.get_platforms(ws_id))

    @namespace.doc("create new service platform")
    def post(self, ws_id):
        return prepare_response(platformsimpl.create_platform(ws_id), 201)


@namespace.route("/<int:platform_id>")
@namespace.param('platform_id', 'The Platform identifier')
@namespace.response(200, "OK")
class Platform(Resource):
    def get(self, ws_id, platform_id):
        return prepare_response(platformsimpl.get_platform(platform_id))

    def put(self, ws_id, platform_id):
        return prepare_response(platformsimpl.update_platform(ws_id, platform_id))

    def delete(self, ws_id, platform_id):
        return prepare_response(platformsimpl.delete(ws_id, platform_id))
