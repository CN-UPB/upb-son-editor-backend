'''
Created on 22.07.2016

@author: Jonas
'''
from flask.globals import session
from flask_restplus import Namespace, Model, fields
from flask_restplus import Resource

from son_editor.impl import nsfslookupimpl
from son_editor.util.constants import WORKSPACES, PROJECTS, NSFS, SERVICES, VNFS
from son_editor.util.requestutil import prepare_response

namespace = Namespace(WORKSPACES + '/<int:ws_id>/' + PROJECTS + '/<int:project_id>/' + NSFS,
                      description="Resource Lookup")
vendor_name_version_path = "/<string:vendor>/<string:name>/<string:version>"

funct = namespace.model("VNF", {
    'name': fields.String(required=True, description='The VNF Name'),
    'vendor': fields.String(required=True, description='The VNF Vendor'),
    'version': fields.String(required=True, description='The VNF Version')

})

serv = namespace.model("Service", {
    'name': fields.String(required=True, description='The Service Name'),
    'vendor': fields.String(required=True, description='The Service Vendor'),
    'version': fields.String(required=True, description='The Service Version')

})

func_response = namespace.inherit("Response", funct, {
    "descriptor": fields.Nested(model=funct, description="The Complete VNF Descriptor"),
    "id": fields.Integer(description='The Project ID'),
    "project_id": fields.Integer(description='The parent project id'),
})

serv_response = namespace.inherit("Response", serv, {
    "descriptor": fields.Nested(model=serv, description="The Complete Service Descriptor"),
    "id": fields.Integer(description='The Project ID'),
    "project_id": fields.Integer(description='The parent project id'),
})


@namespace.route('/' + SERVICES + vendor_name_version_path)
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('project_id', 'The Project identifier')
@namespace.param('vendor', 'The Network Service vendor')
@namespace.param('name', 'The Network Service name')
@namespace.param('version', 'The Network Service version')
class ServiceLookup(Resource):
    @namespace.response(200, "OK", [serv_response])
    def get(self, ws_id, project_id, vendor, name, version):
        """Retrieves a network service by vendor name version

        Finds a specific network service with given vendor / name / version"""
        service = nsfslookupimpl.find_network_service(session["user_data"], ws_id, project_id, vendor, name, version)
        return prepare_response(service)


@namespace.route('/' + VNFS + vendor_name_version_path)
@namespace.param('ws_id', 'The Workspace identifier')
@namespace.param('project_id', 'The Project identifier')
@namespace.param('vendor', 'The Virtual Nework Function vendor')
@namespace.param('name', 'The Virtual Nework Function name')
@namespace.param('version', 'The Virtual Nework Function version')
class FunctionLookup(Resource):
    @namespace.response(200, "OK", [func_response])
    def get(self, ws_id, project_id, vendor, name, version):
        """Retrieves a virtual network function by vendor name version

        Finds a specific virtual network with given vendor / name / version"""
        function = nsfslookupimpl.find_vnf(session["user_data"], ws_id, project_id, vendor, name, version)
        return prepare_response(function)
