import logging

from flask import Response
from flask import request
from flask_restplus import Resource, Namespace

namespace = Namespace("log", description="Log API")
logger = logging.getLogger(__name__)


@namespace.route("")
@namespace.response(200, "OK")
class Log(Resource):
    def get(self):
        """Return the logfile as string"""
        with open("editor-backend-public.log") as logfile:
            return Response(logfile.read().replace("\n", "<br/>"))

