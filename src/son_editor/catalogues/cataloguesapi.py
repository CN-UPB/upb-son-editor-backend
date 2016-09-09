"""
Created on 18.07.2016

@author: Jonas
"""
from flask_restplus import Resource, Namespace

from son_editor.app.util import prepare_response
from son_editor.app.constants import WORKSPACES, CATALOGUES
from son_editor.catalogues import cataloguesimpl

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + CATALOGUES, description="Catalogue Resources")


@namespace.route("/")
@namespace.response(200, "OK")
class Catalogues(Resource):
    "Catalogues"

    @namespace.doc("list catalogues")
    def get(self, ws_id):
        return prepare_response(cataloguesimpl.get_catalogues(ws_id))

    @namespace.doc("create new service catalogue")
    def post(self, ws_id):
        return prepare_response(cataloguesimpl.create_catalogue(ws_id), 201)


@namespace.route("/<int:catalogue_id>")
@namespace.param('catalogue_id', 'The Catalogue identifier')
@namespace.response(200, "OK")
class Catalogue(Resource):
    def get(self, ws_id, catalogue_id):
        return prepare_response(cataloguesimpl.get_catalogue(catalogue_id))

    def put(self, ws_id, catalogue_id):
        return prepare_response(cataloguesimpl.update_catalogue(ws_id, catalogue_id))

    def delete(self, ws_id, catalogue_id):
        return prepare_response(cataloguesimpl.delete(ws_id, catalogue_id))
