'''
Created on 18.07.2016

@author: Jonas
'''
from flask import Flask

from son.editor.app.constants import WORKSPACES, CATALOGUES, PLATFORMS, PROJECTS
from son.editor.app.database import db_session
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


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def hello_world():
    return "hello world!"


'''start the flask service: '''
if __name__ == "__main__":
    app.run()
