"""
Created on 18.07.2016

@author: Jonas
"""
from flask_restplus import Resource, Namespace

from son.editor.app.util import prepare_response
from son.editor.app.constants import WORKSPACES, PLATFORMS

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PLATFORMS, description="Platform Resources")


@namespace.route("")
@namespace.response(200, "OK")
class Platforms(Resource):
    "Platforms"

    #@platforms_api.doc("list platforms")
    def get(self, ws_id):
        return prepare_response([{"id": 1, "name": "platform1"}])

    #@platforms_api.doc("create new service platform")
    def post(self, ws_id, platformID):
        return "create new service platform and return id"


@namespace.route("/<int:platformID>")
@namespace.param('platformID', 'The Platform identifier')
@namespace.response(200, "OK")
class Platform(Resource):
    def get(self, ws_id, platformID):
        return "info for platform with id {}".format(platformID)

    def put(self, ws_id, platformID):
        return "update platform with id {}".format(platformID)

    def delete(self, ws_id, platformID):
        return "deleted platform with id {}".format(platformID)
