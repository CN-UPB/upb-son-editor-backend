import shlex

from flask import session, request
from flask_restplus import Resource, Namespace

from son_editor.impl.gitimpl import clone
from son_editor.util.constants import WORKSPACES
from son_editor.util.requestutil import get_json, prepare_response

namespace = Namespace(WORKSPACES + '/<int:ws_id>/git', description='Git API')


@namespace.route('/clone')
@namespace.response(200, "OK")
class GitClone(Resource):
    def post(self, ws_id):
        """ Clones projects into the workspace """
        json_data = get_json(request)
        result = clone(session["user_data"], ws_id, shlex.quote(json_data['url']))
        return prepare_response(result, 200)


@namespace.route('/pull')
@namespace.response(200, "OK")
class GitPull(Resource):
    def post(self, ws_id):
        """ Clones projects into the workspace """
        json_data = get_json(request)
        result = pull(session["user_data"], ws_id, project_id)
        return prepare_response(result, 200)
