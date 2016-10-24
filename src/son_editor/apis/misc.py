import json
import logging

import requests
from flask import Response
from flask import request, redirect
from flask import session
from flask_restplus import Resource, Namespace

from son_editor.util.requestutil import CONFIG

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


@namespace.route("/login", endpoint="login")
@namespace.response(200, "OK")
class Login(Resource):
    def get(self):
        """ Login the User with a referral code from the github oauth process"""
        session['session_code'] = request.args.get('code')
        if self.request_access_token() and self.load_user_data():
            logger.info("User " + session['userData']['login'] + " logged in")
            if request.referrer is not None and 'github' not in request.referrer:
                origin = self.origin_from_referrer(request.referrer)
                return redirect(origin + CONFIG['frontend-redirect'])
            return redirect(CONFIG['frontend-host'] + CONFIG['frontend-redirect'])

    @staticmethod
    def request_access_token():
        """ Request an access token from Github using the referral code"""
        # TODO add error handling
        data = {'client_id': CONFIG['authentication']['ClientID'],
                'client_secret': CONFIG['authentication']['ClientSecret'],
                'code': session['session_code']}
        headers = {"Accept": "application/json"}
        accessResult = requests.post('https://github.com/login/oauth/access_token',
                                     json=data, headers=headers)
        session['access_token'] = json.loads(accessResult.text)['access_token']
        return True

    @staticmethod
    def load_user_data():
        """Load user data using the access token"""
        # TODO add error handling
        headers = {"Accept": "application/json",
                   "Authorization": "token " + session['access_token']}
        userDataResult = requests.get('https://api.github.com/user', headers=headers)
        userData = json.loads(userDataResult.text)
        session['userData'] = userData
        logger.info("userdata: %s" % userData)
        return True

    @staticmethod
    def origin_from_referrer(referrer):
        doubleSlashIndex = referrer.find("//")
        return referrer[0:referrer.find("/", doubleSlashIndex + 2)]


@namespace.route("/log")
@namespace.response(200, "OK")
class Log(Resource):
    def get(self):
        """Return the logfile as string"""
        with open("editor-backend.log") as logfile:
            return Response(logfile.read().replace("\n", "<br/>"))
