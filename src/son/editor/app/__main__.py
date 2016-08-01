'''
Created on 18.07.2016

@author: Jonas
'''
import json
from sys import platform
from os import path, urandom
import urllib

from flask import Flask, redirect, session, logging
from flask.globals import request
from flask.helpers import url_for
import requests
from sqlalchemy.exc import StatementError

from son.editor.app.constants import WORKSPACES, CATALOGUES, PLATFORMS, PROJECTS, DATABASE_SQLITE_FILE
from son.editor.app.database import db_session, init_db
from son.editor.app.util import CONFIG, prepareResponse
from son.editor.catalogues.cataloguesapi import catalogues_api
from son.editor.platforms.platformsapi import platforms_api
from son.editor.projects.projectsapi import projects_api
from son.editor.services.servicesapi import services_api
from son.editor.vnfs.vnfsapi import vnfs_api
from son.editor.workspaces.workspacesapi import workspaces_api


app = Flask(__name__)
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
# print(app.url_map)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.before_request
def checkLoggedIn():
    if  not 'access_token' in session and request.endpoint != 'login' and request.endpoint != 'static':
        args = {"scope":"user:email",
                "client_id":CONFIG['authentication']['ClientID']}
        session["requested_endpoint"] = request.endpoint
        return prepareResponse({'authorizationUrl':'https://github.com/login/oauth/authorize/?' + urllib.parse.urlencode(args)}), 401

@app.route('/', methods=['GET', 'POST'])
def home():
    # this is only code to test the github login process!
    if 'userData' in session:
        return "<script src='https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js'></script> Welcome " + session['userData']['login'] + "! you are logged in!<br/>" + '<img src="' + session['userData']['avatar_url'] + '">'
    else:
        return redirect('https://github.com/login/oauth/authorize?scope=user:email&client_id=' + CONFIG['authentication']['ClientID'])

@app.route('/login', methods=['GET'])
def login():
    session['session_code'] = request.args.get('code');
    if request_access_token() and load_user_data():
        app.logger.info("User " + session['userData']['login'] + " logged in")
        # return redirect(url_for(session["requested_endpoint"]))
        return redirect(url_for("home"))

def request_access_token():
    # TODO add error handling
    data = {'client_id':     CONFIG['authentication']['ClientID'],
            'client_secret': CONFIG['authentication']['ClientSecret'],
            'code':          session['session_code']}
    headers = {"Accept": "application/json"}
    accessResult = requests.post('https://github.com/login/oauth/access_token',
                           json=data, headers=headers)
    session['access_token'] = json.loads(accessResult.text)['access_token']
    return True

def load_user_data():
    # TODO add error handling
    headers = {"Accept": "application/json",
               "Authorization": "token " + session['access_token']}
    userDataResult = requests.get('https://api.github.com/user' , headers=headers)
    userData = json.loads(userDataResult.text)
    session['userData'] = userData
    return True

# Main entry point
def main(args=None):
    # Check check if database exists, otherwise create sqlite file
    if path.exists(DATABASE_SQLITE_FILE):
        print('Using database file "%s"' % DATABASE_SQLITE_FILE)
    else:
        print('Init database on "%s"' % DATABASE_SQLITE_FILE)
        init_db()

    # Start the flask server
    print("Launch flask server")
    if platform == "darwin":
        app.run('0.0.0.0', debug=True)
    else:
        app.run('0.0.0.0')


if __name__ == "__main__":
    main()
