import logging

from flask import Response
from flask import request
from flask_restplus import Resource, Namespace

namespace = Namespace("", description="Misc API")
logger = logging.getLogger(__name__)


@namespace.route("/shutdown", endpoint="shutdown")
@namespace.response(200, "OK")
class Shutdown(Resource):
    def get(self):
        """ Shutdown the server

        Only works if issued from localhost"""
        if request.remote_addr in ['127.0.0.1', 'localhost']:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            logger.info("Shutting down!")
            func()
            return "Shutting down..."
        return "Not allowed to perform this action"


@namespace.route("/log")
@namespace.response(200, "OK")
class Log(Resource):
    def get(self):
        """Return the logfile as string"""
        with open("editor-backend.log") as logfile:
            return Response(logfile.read().replace("\n", "<br/>"))
