'''
Created on 18.07.2016

@author: Jonas
'''
import json
import logging
import urllib
from os import path
from sys import platform

import requests
from flask import Flask, redirect, session
from flask.globals import request

from son.editor.app.exceptions import NameConflict, NotFound

from son.editor.app.constants import WORKSPACES, CATALOGUES, PLATFORMS, PROJECTS
from son.editor.app.database import db_session, init_db
from son.editor.app.util import CONFIG, prepareResponse
from son.editor.catalogues.cataloguesapi import catalogues_api
from son.editor.platforms.platformsapi import platforms_api
from son.editor.projects.projectsapi import projects_api
from son.editor.services.servicesapi import services_api
from son.editor.vnfs.functionsapi import vnfs_api
from son.editor.workspaces.workspacesapi import workspaces_api

app = Flask(__name__)
logger = logging.getLogger("son-editor.__main__")

WORKSPACE_PATH = '/' + WORKSPACES + '/<wsID>/'

# registering all the to class modules here
app.register_blueprint(workspaces_api)
app.register_blueprint(projects_api)
app.register_blueprint(services_api, url_prefix=WORKSPACE_PATH + PROJECTS)
app.register_blueprint(vnfs_api, url_prefix=WORKSPACE_PATH + PROJECTS)
app.register_blueprint(platforms_api)
app.register_blueprint(services_api, url_prefix=WORKSPACE_PATH + PLATFORMS)
app.register_blueprint(vnfs_api, url_prefix=WORKSPACE_PATH + PLATFORMS)
app.register_blueprint(catalogues_api)
app.register_blueprint(services_api, url_prefix=WORKSPACE_PATH + CATALOGUES)
app.register_blueprint(vnfs_api, url_prefix=WORKSPACE_PATH + CATALOGUES)
# load secret key from config
app.secret_key = CONFIG['session']['secretKey']


# Set initial testing flag to false

# print(app.url_map)



@app.errorhandler(KeyError)
def handle_key_error(err):
    logger.exception(err.args[0])
    return prepareResponse("Key '{}' is required in request data!".format(err.args[0])), 400


@app.errorhandler(NotFound)
def handle_not_found(err):
    logger.warn(err.msg)
    return prepareResponse(err.msg), 404


@app.errorhandler(NameConflict)
def handle_name_conflict(err):
    logger.warn(err.msg)
    return prepareResponse(err.msg), 409


@app.errorhandler(Exception)
def handle_general_exception(err):
    logger.exception(err.args[0])
    return prepareResponse(str(err.args)), 500


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.before_request
def checkLoggedIn():
    if request.method == 'OPTIONS':
        return prepareResponse()
    elif CONFIG['testing']:
        return
    elif 'access_token' not in session and request.endpoint not in ['login', 'static', 'shutdown']:
        args = {"scope": "user:email",
                "client_id": CONFIG['authentication']['ClientID']}
        session["requested_endpoint"] = request.endpoint
        return prepareResponse(
            {'authorizationUrl': 'https://github.com/login/oauth/authorize/?' + urllib.parse.urlencode(args)}), 401


@app.route('/', methods=['GET', 'POST'])
def home():
    # this is only code to test the github login process!
    if 'userData' in session:
        return "<script src='https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js'></script> Welcome " + \
               session['userData']['login'] + "! you are logged in!<br/>" + '<img src="' + session['userData'][
                   'avatar_url'] + '">'
    else:
        return redirect(
            'https://github.com/login/oauth/authorize?scope=user:email&client_id=' + CONFIG['authentication'][
                'ClientID'])


@app.route('/shutdown', methods=['GET'])
def shutdown():
    if request.remote_addr in ['127.0.0.1', 'localhost']:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        logger.info("Shutting down!")
        func()
        return "Shutting down..."


@app.route('/login', methods=['GET'])
def login():
    session['session_code'] = request.args.get('code');
    if request_access_token() and load_user_data():
        logger.info("User " + session['userData']['login'] + " logged in")
        if request.referrer is not None and 'github' not in request.referrer:
            origin = origin_from_referrer(request.referrer)
            return redirect(origin + CONFIG['frontend-redirect'])
        return redirect(CONFIG['frontend-host'] + CONFIG['frontend-redirect'])


def origin_from_referrer(referrer):
    doubleSlashIndex = referrer.find("//")
    return referrer[0:referrer.find("/", doubleSlashIndex + 2)]


def request_access_token():
    # TODO add error handling
    data = {'client_id': CONFIG['authentication']['ClientID'],
            'client_secret': CONFIG['authentication']['ClientSecret'],
            'code': session['session_code']}
    headers = {"Accept": "application/json"}
    accessResult = requests.post('https://github.com/login/oauth/access_token',
                                 json=data, headers=headers)
    session['access_token'] = json.loads(accessResult.text)['access_token']
    return True


def load_user_data():
    # TODO add error handling
    headers = {"Accept": "application/json",
               "Authorization": "token " + session['access_token']}
    userDataResult = requests.get('https://api.github.com/user', headers=headers)
    userData = json.loads(userDataResult.text)
    session['userData'] = userData
    logger.info("userdata: %s" % userData)
    return True

@app.route("/log")
def show_log():
    with open("editor-backend.log") as logfile:
        return logfile.read().replace("\n", "<br/>")


# Main entry point
def main(args=None):
    setup_logging()
    # Check check if database exists, otherwise create sqlite file
    dbFile = CONFIG['database']['location']
    if path.exists(dbFile):
        logger.info('Using database file "%s"' % dbFile)
    else:
        logger.info('Init database on "%s"' % dbFile)
        init_db()

    # Start the flask server
    logger.info("Launch flask server")
    if platform == "darwin":
        app.run('0.0.0.0', debug=True)
    else:
        app.run('0.0.0.0')


def setup_logging():
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='editor-backend.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


if __name__ == "__main__":
    main()
