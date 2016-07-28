'''
Created on 28.07.2016

@author: Jonas
'''
import json

from flask.wrappers import Response


def prepareResponse(data):
    response = Response(json.dumps(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response