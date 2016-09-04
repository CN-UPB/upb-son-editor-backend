'''
Created on 18.07.2016

@author: Jonas
'''
from flask_restplus import Resource, Namespace

from son.editor.app.constants import WORKSPACES, CATALOGUES

namespace = Namespace(WORKSPACES + "/<int:ws_id>/" + CATALOGUES, description="Catalogue Resources")


@namespace.route("/")
class Catalogues(Resource):
    def get(self, ws_id):
        return "list of catalogues"

    def post(self, ws_id):
        return "create new catalogue and return id"


@namespace.route('/<int:catalogueID>')
class Catalogue(Resource):
    def get(self, ws_id, catalogueID):
        return "get catalogue with id {}".format(catalogueID)

    def put(self, ws_id, catalogueID):
        return "update catalogue with id {}".format(catalogueID)

    def delete(self, ws_id, catalogueID):
        return "deleted catalogue with id {}".format(catalogueID)
