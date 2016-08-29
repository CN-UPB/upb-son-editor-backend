import json
import unittest

from son.editor.app.constants import WORKSPACES, PROJECTS
from son.editor.app.database import db_session
from son.editor.models.user import User
from son.editor.models.workspace import Workspace
from son.editor.util.context import init_test_context


class ProjectTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()


        # Add some session stuff ( need for finding the user's workspace )
        with self.app as c:
            with c.session_transaction() as session:
                session['userData'] = {'login': 'user'}

        # Add some dummy objects
        self.user = User(name="user", email="foo@bar.com")

        # Add some relationships
        db_session.add(self.user)
        db_session.commit()
        # Create real workspace by request
        request_dict = {"name": "ProjectTest"}
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json',
                           follow_redirects=True)
        self.wsid = json.loads(rv.data.decode())['id']

        self.workspace = db_session.query(Workspace).filter_by(id=self.wsid).first()
        db_session.commit()
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(rv.data.decode())['name'])

    def tearDown(self):
        rv = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid))
        db_session.delete(self.user)
        db_session.commit()

    def test_create_project(self):
        # Setup request dict
        request_dict = {"name": "projectName"}

        # Post request on projects
        rv = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                           data=json.dumps(request_dict), content_type='application/json',
                           follow_redirects=True)
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(rv.data.decode())['name'])
        self.assertEqual(201, rv.status_code)

    # Create project
    def test_get_projects(self):
        request_dict = {"name": "projectName1"}

        # Post request on projects
        rv = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                           data=json.dumps(request_dict), content_type='application/json',
                           follow_redirects=True)

        # Post request on projects
        rv = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/')

        result = json.loads(rv.data.decode())
        self.assertEqual(result[0]['name'], request_dict['name'])
