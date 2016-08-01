'''
Created on 28.07.2016

@author: Jonas
'''
import json

from flask.wrappers import Response
from pkg_resources import Requirement, resource_filename
import yaml


configFileName = resource_filename(Requirement.parse("sonata_editor"), "config.yaml")
CONFIG = yaml.safe_load(open(str(configFileName)))

def prepareResponse(data):
    response = Response(json.dumps(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['contentType'] = 'application/json'
    return response
