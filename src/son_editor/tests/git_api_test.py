import json
import logging
import unittest

from son_editor.models.project import Project
from son_editor.tests.utils import *
from son_editor.util.context import init_test_context
from son_editor.util.requestutil import get_config

logger = logging.getLogger(__name__)

GITHUB_URL = "http://github.com"
REMOTE_REPO_NAME = 'test_create'
REMOTE_INVALID_REPO_NAME = 'invalid-son-repo'

CONFIG = get_config()

# Check if there exist testing entries in environment (for travis configuration), otherwise use config.yaml

if 'github_bot_user' in os.environ and "github_access_token" in os.environ:
    GITHUB_USER = os.environ["github_bot_user"]
    GITHUB_ACCESS_TOKEN = os.environ["github_access_token"]
elif 'test' in CONFIG and 'github' in CONFIG['test'] and 'user' in CONFIG['test']['github'] and 'access-token' in \
        CONFIG['test']['github']:
    GITHUB_USER = CONFIG['test']['github']['user']
    GITHUB_ACCESS_TOKEN = CONFIG['test']['github']['access-token']


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
        self.pjid = str(create_project(int(self.wsid), 'ProjectA'))
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
        # set url on project to be able to delete
        dbsession = db_session()
        dbsession.query(Project).filter(Project.id == self.pjid) \
            .first().repo_url = GITHUB_URL + "/" + GITHUB_USER + "/" + REMOTE_REPO_NAME
        dbsession.commit()
        # Clean github repository
        arg = {'project_id': self.pjid, 'repo_name': REMOTE_REPO_NAME}
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/delete",
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(arg))

    def call_github_post(self, git_method: str, arg: dict):
        response = self.app.post(
            "/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/{}".format(git_method),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(arg))
        return response

    def assertResponseValid(self, response):
        """ Asserts that the response is valid"""
        self.assertTrue(response.status_code, 200)

    def assertInvalidArgument(self, response):
        """ Asserts that the response is invalid"""
        self.assertTrue(response.status_code, 400)

    def test_init_and_create_remote_repo(self):
        # 1. init git repository in the given project
        arg = {'project_id': self.pjid}
        response = self.call_github_post('init', arg)
        self.assertResponseValid(response)

        # 2. Create and push git repository
        arg = {'project_id': self.pjid, 'repo_name': REMOTE_REPO_NAME}
        response = self.call_github_post('create', arg)
        self.assertResponseValid(response)

    def test_clone_and_delete_repo(self):
        # 1. Init and create remote repo
        self.test_init_and_create_remote_repo()

        # Check if repository was created, by using list function
        response = self.app.get("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/list")

        # Look for newly created project
        for i in json.loads(response.data.decode()):
            if i['name'] == REMOTE_REPO_NAME:
                clone_url = i['clone_url']

        self.assertTrue(clone_url is not None)

        arg = {'url': clone_url}
        response = self.call_github_post('clone', arg)
        self.assertResponseValid(response)
        json_data = json.loads(response.data.decode())
        arg = {'project_id': json_data['id'], 'repo_name': REMOTE_REPO_NAME}

        response = self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.GIT + "/delete",
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(arg))
        self.assertResponseValid(response)

    def test_clone_invalid_son_repo(self):
        # Format invalid project url
        arg = {'url': '{}/{}/{}'.format(GITHUB_URL, GITHUB_USER, REMOTE_INVALID_REPO_NAME)}
        response = self.call_github_post('clone', arg)
        self.assertInvalidArgument(response)

        # Invalid url
        arg = {'url': 'localhost'}
        response = self.call_github_post('clone', arg)
        self.assertInvalidArgument(response)
