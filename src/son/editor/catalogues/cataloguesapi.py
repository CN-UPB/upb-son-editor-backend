'''
Created on 18.07.2016

@author: Jonas
'''
from flask_restplus import Resource, Namespace

from son.editor.app.constants import WORKSPACES, CATALOGUES

namespace = Namespace(WORKSPACES + "/<int:wsID>/" + CATALOGUES, description="Catalogue Resources")


@namespace.route("/")
class Catalogues(Resource):
    def get(self, wsID):
        return "list of catalogues"

    def post(self, wsID):
        return "create new catalogue and return id"


@namespace.route('/<int:catalogueID>')
class Catalogue(Resource):
    def get(self, wsID, catalogueID):
        return "get catalogue with id {}".format(catalogueID)

    def put(self, wsID, catalogueID):
        return "update catalogue with id {}".format(catalogueID)

    def delete(self, wsID, catalogueID):
        return "deleted catalogue with id {}".format(catalogueID)
