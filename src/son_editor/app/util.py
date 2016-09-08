'''
Created on 28.07.2016

@author: Jonas
'''
import json

from flask import request
from flask.wrappers import Response
from pkg_resources import Requirement, resource_string
import yaml
CONFIG = yaml.safe_load(resource_string(Requirement.parse("upb-son-editor-backend"), "son_editor/config.yaml"))


def prepare_response(data=None, code=200):
    response = Response()
    headers = response.headers
    if allowed_origin():
        headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    headers['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS"
    headers['Access-Control-Allow-Headers'] = "Content-Type, Authorization, X-Requested-With"
    headers['Access-Control-Allow-Credentials'] = "true"
    headers['Access-Control-Max-Age'] = 1000
    if data is not None:
        if isinstance(data, dict) or isinstance(data, list):
            response.set_data(json.dumps(data))
            headers['Content-Type'] = 'application/json'
        else:
            response.set_data(data)
            headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.status_code = code
    return response


def prepare_error(data=None, code=500):
    response = Response()
    headers = response.headers
    if allowed_origin():
        headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    headers['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS"
    headers['Access-Control-Allow-Headers'] = "Content-Type, Authorization, X-Requested-With"
    headers['Access-Control-Allow-Credentials'] = "true"
    headers['Access-Control-Max-Age'] = 1000
    return data, code, headers


def allowed_origin():
    if 'Origin' in request.headers:
        origin = request.headers['Origin'].replace("http://", "").replace("https://", "")
        origin_parts = origin.split(":")
        if len(origin_parts) > 1:
            origin = origin_parts[0]
        return origin in CONFIG['allowed-hosts']


def get_json(request):
    json_data = request.get_json()
    if json_data is None:
        json_data = request.form
    if json_data is None:
        json_data = json.loads(request.get_data().decode("utf8"))
    return json_data


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)
