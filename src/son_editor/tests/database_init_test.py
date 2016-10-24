import json
import unittest

from son_editor.app.database import db_session, reset_db, scan_workspaces_dir
from son_editor.models.user import User
from son_editor.util.constants import WORKSPACES, PROJECTS
from son_editor.util.context import init_test_context
from son_editor.tests.utils import *


class ProjectTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Add user
        self.user = create_logged_in_user(self.app, 'user')
        # Create real workspace by request
        request_dict = {"name": "test_ws"}
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        request_dict = {"name": "test_pj"}
        rv = self.app.post('/' + WORKSPACES + '/' + PROJECTS + '/', data=json.dumps(request_dict),
                           content_type='application/json')

    @staticmethod
    def test_scan_workspace():
        reset_db()
        scan_workspaces_dir()
