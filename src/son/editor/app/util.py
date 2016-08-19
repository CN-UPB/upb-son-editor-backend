'''
Created on 28.07.2016

@author: Jonas
'''
import json

from flask import request
from flask.wrappers import Response
from pkg_resources import Requirement, resource_filename
import yaml

configFileName = resource_filename(Requirement.parse("sonata_editor"), "config.yaml")
CONFIG = yaml.safe_load(open(str(configFileName)))


def prepareResponse(data=None):
    response = Response()
    headers = response.headers
    if allowed_origin():
        headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    headers['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS"
    headers['Access-Control-Allow-Headers'] = "Content-Type, Authorization, X-Requested-With"
    headers['Access-Control-Allow-Credentials'] = "true"
    headers['Access-Control-Max-Age'] = 1000
    if data is not None:
        if type(data) is dict or type(data) is list:
            response.set_data(json.dumps(data))
            headers['Content-Type'] = 'application/json'
        else:
            response.set_data(data)
            headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers = headers
    return response


def allowed_origin():
    if 'Origin' in request.headers:
        origin = request.headers['Origin'].replace("http://", "").replace("https://", "")
        origin_parts = origin.split(":")
        if len(origin_parts) > 1:
            origin = origin_parts[0]
        return origin in CONFIG['allowed-hosts']


def getJSON(request):
    jsonData = request.get_json()
    if jsonData is None:
        jsonData = request.form
    if jsonData is None:
        jsonData = json.loads(request.get_data().decode("utf8"))
    return jsonData
