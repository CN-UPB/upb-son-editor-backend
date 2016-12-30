import shlex

from flask import session, request
from flask_restplus import Resource, Namespace, fields

from son_editor.impl.gitimpl import clone, pull, commit_and_push, create
from son_editor.util.constants import WORKSPACES
from son_editor.util.requestutil import get_json, prepare_response

namespace = Namespace(WORKSPACES + '/<int:ws_id>/git', description='Git API')

pull_model = namespace.model('Pull information', {
    'project_id': fields.Integer(description='Project ID of the project to get pulled from')
})

clone_model = namespace.model('Clone information', {
    'url': fields.String(description='URL to clone from')
})

commit_model = namespace.model('Commit information', {
    'project_id': fields.Integer(description='Project ID for making commit'),
    'commit_message': fields.String(description='Commit message')
})

create_model = namespace.model('Create GitHub repository information', {
    'project_id': fields.Integer(description='Project ID for the project to push'),
    'repo_name': fields.String(description='Remote repository name for the project, that gets created')
})

response_model = namespace.model('Model response', {
    'success': fields.Boolean(description='True, if the operation was successful, otherwise false'),
    'message': fields.String(description='Reason'),
    'exitcode': fields.Integer(description='Exitcode of git')
})

exception_model = namespace.model('Exception response', {
    'message': fields.String()
})


@namespace.route('/clone')
class GitClone(Resource):
    @namespace.expect(clone_model)
    @namespace.response(200, "OK", response_model)
    @namespace.response(404, "When workspace not found", exception_model)
    @namespace.response(409, "When project already exists", exception_model)
    def post(self, ws_id):
        """ Clones projects into the workspace """
        json_data = get_json(request)
        result = clone(session["user_data"], ws_id, shlex.quote(json_data['url']))
        return prepare_response(result, 200)


@namespace.route('/commit')
class GitCommit(Resource):
    @namespace.expect(commit_model)
    @namespace.response(200, "OK", response_model)
    @namespace.response(404, "When project or workspace not found", exception_model)
    def post(self, ws_id):
        """ Commits and pushes changes """
        json_data = get_json(request)
        result = commit_and_push(ws_id, shlex.quote(json_data['project_id']), shlex.quote(json_data['commit_message']))
        return prepare_response(result, 200)


@namespace.route('/create')
class GitCreate(Resource):
    @namespace.expect(create_model)
    @namespace.response(201, "When project got created and push went fine")
    @namespace.response(404, "When project or workspace not found", exception_model)
    def post(self, ws_id):
        """ Creates a remote repository and pushes a project for it"""
        json_data = get_json(request)
        result = create(ws_id, shlex.quote(json_data['project_id']), shlex.quote(json_data['repo_name']))
        return prepare_response(result)


@namespace.route('/pull')
class GitPull(Resource):
    @namespace.expect(pull_model)
    @namespace.response(200, "OK", response_model)
    @namespace.response(404, "When project or workspace not found", exception_model)
    def post(self, ws_id):
        """ Pulls updates from a project """
        json_data = get_json(request)
        result = pull(ws_id, json_data['project_id'])
        return prepare_response(result, 200)
