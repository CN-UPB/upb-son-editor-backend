from flask_restplus import Resource, Namespace, fields

from son_editor.util.requestutil import get_config, update_config
from flask import request, Response
from son_editor.util.requestutil import prepare_response, get_json

namespace = Namespace("config", description="Configuration")


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if 'config' in get_config():
        if 'user' in get_config()['config'] and 'pwd' in get_config()['config']:
            return username == get_config()['config']['user'] and password == get_config()['config']['pwd']
    return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


config_model = namespace.model("Config", {})


@namespace.route("")
class Configuration(Resource):
    @requires_auth
    def get(self):
        return prepare_response(get_config())

    @namespace.expect(config_model)
    def post(self):
        update_config(get_json(request))
