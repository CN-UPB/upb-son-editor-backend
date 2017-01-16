import unittest
import json

from son_editor.tests.utils import *
from son_editor.util.requestutil import CONFIG
from son_editor.util.context import init_test_context

# Get access token

github_user = os.environ["github_bot_user"] if not CONFIG['github_bot_user'] else CONFIG['github_bot_user']
github_access_token = os.environ["github_access_token"] if not CONFIG['github_access_token'] else CONFIG[
    'github_access_token']


class GitAPITest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Add some session stuff ( need for finding the user's workspace )
        if not github_user:
            self.username = "dummy"
        else:
            self.username = github_user
        self.user = create_logged_in_user(self.app, self.username, github_access_token)
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
        # Clean github repository
        arg = {'repo_name': 'test_create'}
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/delete",
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(arg))

    def test_create_remote_project(self):
        # 1. init git repository in the given project

        arg = {'project_id': self.pjid}
        response = self.app.post("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/init",
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps(arg))
        json_data = json.loads(response.data.decodeO())
        self.assertTrue(json_data['success'], "true")

        # 2. Create and push git repository
        arg = {'project_id': self.pjid, 'repo_name': 'test_create'}

        response = self.app.post("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/create",
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps(arg))
        json_data = json.loads(response.data.decode())
        self.assertTrue(json_data['success'], "true")
