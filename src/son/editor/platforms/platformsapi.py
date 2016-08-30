"""
Created on 18.07.2016

@author: Jonas
"""
from flask_restplus import Resource, Namespace

from son.editor.app.util import prepareResponse
from son.editor.app.constants import WORKSPACES, PLATFORMS

namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PLATFORMS, description="Platform Resources")


@namespace.route("")
@namespace.response(200, "OK")
class Platforms(Resource):
    "Platforms"

    #@platforms_api.doc("list platforms")
    def get(self, wsID):
        return prepareResponse([{"id": 1, "name": "platform1"}])

    #@platforms_api.doc("create new service platform")
    def post(self, wsID, platformID):
        return "create new service platform and return id"


@namespace.route("/<int:platformID>")
@namespace.param('platformID', 'The Platform identifier')
@namespace.response(200, "OK")
class Platform(Resource):
    def get(self, wsID, platformID):
        return "info for platform with id {}".format(platformID)

    def put(self, wsID, platformID):
        return "update platform with id {}".format(platformID)

    def delete(self, wsID, platformID):
        return "deleted platform with id {}".format(platformID)
