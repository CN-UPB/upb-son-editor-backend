"""
Created on 18.07.2016

@author: Jonas
"""
from flask_restplus import Resource, Namespace

from son_editor.impl import cataloguesimpl
from son_editor.util.constants import WORKSPACES, CATALOGUES
from son_editor.util.requestutil import prepare_response

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + CATALOGUES, description="Catalogue Resources")


@namespace.route("/")
@namespace.response(200, "OK")
class Catalogues(Resource):
    "Catalogues"

    def get(self, ws_id):
        """Lists catalogues

        Lists catalogues in a specific workspace"""
        return prepare_response(cataloguesimpl.get_catalogues(ws_id))

    def post(self, ws_id):
        """Creates a new service catalogue

        Creates a new service catalogue in the specific workspace"""
        return prepare_response(cataloguesimpl.create_catalogue(ws_id), 201)


@namespace.route("/<int:catalogue_id>")
@namespace.param('catalogue_id', 'The Catalogue identifier')
@namespace.response(200, "OK")
class Catalogue(Resource):
    def get(self, ws_id, catalogue_id):
        """Gets a specific catalogue

        Gets a specifc catalogue by its id """
        return prepare_response(cataloguesimpl.get_catalogue(catalogue_id))

    def put(self, ws_id, catalogue_id):
        """Updates a specific catalogue

        Updates a specific catalogue by its id"""
        return prepare_response(cataloguesimpl.update_catalogue(ws_id, catalogue_id))

    @namespace.doc()
    def delete(self, ws_id, catalogue_id):
        """Deletes a specific catalogue

        Deletes a catalogue by its id"""
        return prepare_response(cataloguesimpl.delete(ws_id, catalogue_id))
