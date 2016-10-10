import json
import unittest

from son.workspace.workspace import Workspace
from son_editor.app.database import db_session, reset_db, init_db, scan_workspaces_dir
from son_editor.models.user import User
from son_editor.util.constants import WORKSPACES
from son_editor.util.context import init_test_context


class ProjectTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()

        # Add some session stuff ( need for finding the user's workspace )
        with self.app as c:
            with c.session_transaction() as session:
                session['userData'] = {'login': 'user'}

        # Add user
        self.user = User(name="user", email="foo@bar.com")
        db_session.add(self.user)
        db_session.commit()
        # Create real workspace by request
        request_dict = {"name": "test_ws"}
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        request_dict = {"name": "test_pj"}
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')

    @staticmethod
    def test_scan_workspace():
        reset_db()
        scan_workspaces_dir()
