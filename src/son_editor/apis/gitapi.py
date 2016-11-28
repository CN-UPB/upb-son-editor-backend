import shlex

from flask import session, request
from flask_restplus import Resource, Namespace

from son_editor.impl.gitimpl import create
from son_editor.util.constants import WORKSPACES
from son_editor.util.requestutil import get_json, prepare_response

namespace = Namespace(WORKSPACES + '/<int:ws_id>', description='Git API')


@namespace.route('/git')
@namespace.response(200, "OK")
class Git(Resource):
    def post(self, ws_id):
        """ Clones a project into the workspace """
        json_data = get_json(request)
        result = create(session["user_data"], ws_id, shlex.quote(json_data['url']))
        return prepare_response(result, 200)
