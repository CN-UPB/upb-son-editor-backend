'''
Created on 22.07.2016

@author: Jonas
'''
from flask.globals import request, session
from flask_restplus import Namespace
from flask_restplus import Resource

from son.editor.app.constants import get_parent, Category, WORKSPACES, PROJECTS, CATALOGUES, PLATFORMS, VNFS
from son.editor.app.util import prepareResponse, getJSON
from son.editor.vnfs import functionsimpl

proj_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PROJECTS + "/<int:parentID>/" + VNFS,
                           description="Project VNF Resources")
cata_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + CATALOGUES + "/<int:parentID>/" + VNFS,
                           description="Catalogue VNF Resources")
plat_namespace = Namespace(WORKSPACES + '/<int:wsID>/' + PLATFORMS + "/<int:parentID>/" + VNFS,
                           description="Platform VNF Resources")


@proj_namespace.route('/')
@cata_namespace.route('/')
@plat_namespace.route('/')
class Functions(Resource):
    def get(self, wsID, parentID):
        if get_parent(request) is Category.project:
            functions = functionsimpl.get_functions(session["userData"], wsID, parentID)
            return prepareResponse(functions)
        return prepareResponse("not yet implemented")

    def post(self, wsID, parentID):
        if get_parent(request) is Category.project:
            vnf_data = getJSON(request)
            vnf_data = functionsimpl.create_function(session['userData'], wsID, parentID, vnf_data)
            return prepareResponse(vnf_data, 201)
        # TODO implement for catalog and platform
        return prepareResponse("not implemented yet")


@proj_namespace.route('/<int:vnf_id>')
@cata_namespace.route('/<int:vnf_id>')
@plat_namespace.route('/<int:vnf_id>')
class Function(Resource):
    def put(self, wsID, parentID, vnf_id):
        if get_parent(request) is Category.project:
            vnf_data = getJSON(request)
            vnf_data = functionsimpl.update_function(session['userData'], wsID, parentID, vnf_id, vnf_data)
            return prepareResponse(vnf_data)
        return prepareResponse("update vnf in project with id " + parentID)

    def delete(self, wsID, parentID, vnf_id):
        deleted = functionsimpl.delete_function(session['userData'], wsID, parentID, vnf_id)
        return prepareResponse(deleted)

    def get(self, wsID, parentID, vnf_id):
        if get_parent(request) is Category.project:
            functions = functionsimpl.get_specific_function(session["userData"], wsID, parentID, vnf_id)
            return prepareResponse(functions)
        return prepareResponse("not yet implemented")
