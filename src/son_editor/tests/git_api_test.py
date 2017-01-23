import json
import unittest
import time

from son_editor.tests.utils import *
from son_editor.util.context import init_test_context
from son_editor.util.requestutil import CONFIG

# Get the github_bot_user / github_access_token from the CONFIG,
# otherwise take it from the environment variable (which should be set on travis)

self.remote_repo_name = 'test_create'

GITHUB_USER = os.environ["github_bot_user"] if not 'github_bot_user' in CONFIG else CONFIG['github_bot_user']
GITHUB_ACCESS_TOKEN = os.environ["github_access_token"] if not 'github_access_token' in CONFIG else CONFIG[
    'github_access_token']


class GitAPITest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Add some session stuff ( need for finding the user's workspace )
        if not GITHUB_USER:
            self.username = 'dummy'
        else:
            self.username = GITHUB_USER
        # Name constant


        self.user = create_logged_in_user(self.app, self.username, GITHUB_ACCESS_TOKEN)
        # Create a workspace and project
        self.wsid = str(create_workspace(self.user, 'WorkspaceA'))
        # Create sample project
        self.pjid = str(create_project(self.wsid, 'ProjectA'))
        self.clean_github()

    def tearDown(self):
        self.clean_github()
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.PROJECTS + "/" + self.pjid)
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid)
        # Delete user
        dbsession = db_session()
        user = dbsession.query(User).filter(User.name == self.username).first()
        dbsession.delete(user)
        dbsession.commit()

    def clean_github(self):
        """ Deletes the created test project(s) on github """
        # Clean github repository
        arg = {'repo_name': self.remote_repo_name}
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/delete",
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(arg))

    def call_github_post(self, gitmethod: str, arg: dict):
        response = self.app.post(
            "/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/{}".format(gitmethod),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(arg))
        return response

    def assertResponseValid(self, response):
        json_data = json.loads(response.data.decode())
        self.assertTrue(json_data['success'], "true")

    def test_init_and_create_remote_repo(self):
        # 1. init git repository in the given project
        arg = {'project_id': self.pjid}
        response = self.call_github_post('init', arg)
        self.assertResponseValid(response)

        # 2. Create and push git repository
        arg = {'project_id': self.pjid, 'repo_name': self.remote_repo_name}
        response = self.call_github_post('create', arg)
        self.assertResponseValid(response)

    def test_clone_and_delete_repo(self):
        # Init and create remote repo
        self.test_init_and_create_remote_repo()

        response = self.app.get("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/list")

        # List functionality
        arg = {'url': json.loads(response.data.decode())[0]['clone_url']}

        response = self.call_github_post('clone', arg)
        self.assertResponseValid(response)

        arg = {'repo_name': self.remote_repo_name}
        response = self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/delete",
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(arg))
        self.assertResponseValid(response)
