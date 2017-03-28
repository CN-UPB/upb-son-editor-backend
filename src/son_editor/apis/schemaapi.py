import logging

from flask import Response
from flask import request
from flask_restplus import Resource, Namespace

from son_editor.impl import workspaceimpl
from son_editor.util import descriptorutil
from son_editor.util.constants import WORKSPACES
from son_editor.util.descriptorutil import SCHEMA_ID_VNF
from son_editor.util.requestutil import prepare_response, get_config

namespace = Namespace(WORKSPACES + "/<int:ws_id>/schema", description="Schema API")
logger = logging.getLogger(__name__)


@namespace.route("/<schema_id>")
class Schema(Resource):
    """
    Single schema retrieval
    """

    def get(self, ws_id, schema_id):
        """
        Return the requested schema

        :param ws_id:
        :param schema_id:
        :return:
        """
        schema_index = workspaceimpl.get_workspace(ws_id)['schema_index']
        return prepare_response(descriptorutil.get_schema(schema_index, schema_id))


@namespace.route("/")
class Schemas(Resource):
    """Get all schemas for this server"""

    def get(self, ws_id):
        """
        List Schemas
        
        Returns a list of all schemas configured for this server

        :param ws_id:
        :return:
        """
        return prepare_response(get_config()["schemas"])
