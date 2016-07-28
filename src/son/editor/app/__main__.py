'''
Created on 18.07.2016

@author: Jonas
'''
import json
from os import path

from flask import Flask, redirect, session
from flask.globals import request
import requests
import yaml

from son.editor.app.constants import WORKSPACES, CATALOGUES, PLATFORMS, PROJECTS, DATABASE_SQLITE_FILE
from son.editor.app.database import db_session, init_db
from son.editor.catalogues.cataloguesapi import catalogues_api
from son.editor.platforms.platformsapi import platforms_api
from son.editor.projects.projectsapi import projects_api
from son.editor.services.servicesapi import services_api
from son.editor.vnfs.vnfsapi import vnfs_api
from son.editor.workspaces.workspacesapi import workspaces_api


app = Flask(__name__)
WORKSPACE_PATH = '/' + WORKSPACES + '/<wsID>/'
CONFIG = yaml.safe_load(open("config.yaml"))


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


@app.route('/', methods=['GET', 'POST'])
def home():
    # this is only code to test the github login process!
    if True:
        print(request.method)
        return "test"
    if 'access_token' in session:
        headers = {"Accept": "application/json"}
        result = requests.get('https://api.github.com/user?access_token=' + session['access_token'], headers=headers)
        userData = json.loads(result.text)
        session['userData'] = userData
        return "Welcome " + userData['login'] + "! you are logged in!<br/>" + '<img src="' + userData['avatar_url'] + '">'
    else:
        return redirect('https://github.com/login/oauth/authorize?scope=user:email&client_id=' + CONFIG['authentication']['ClientID'])

@app.route('/login', methods=['GET'])
def login():
    session['session_code'] = request.args.get('code');
    data = {'client_id':     CONFIG['authentication']['ClientID'],
            'client_secret': CONFIG['authentication']['ClientSecret'],
            'code':          session['session_code']}
    headers = {"Accept": "application/json"}
    result = requests.post('https://github.com/login/oauth/access_token',
                           json=data, headers=headers)
    session['access_token'] = json.loads(result.text)['access_token']
    print(session['access_token'])
    return redirect(CONFIG['frontend-home'])

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
    app.run('0.0.0.0')


if __name__ == "__main__":
    main()
