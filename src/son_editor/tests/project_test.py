import json
import unittest

from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util.constants import WORKSPACES, PROJECTS
from son_editor.util.context import init_test_context


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
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        self.wsid = json.loads(rv.data.decode())['id']

        self.workspace = db_session.query(Workspace).filter_by(id=self.wsid).first()
        db_session.commit()
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(rv.data.decode())['name'])

    def tearDown(self):
        rv = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid))
        db_session.delete(self.user)
        db_session.commit()

    # Create project
    def test_create_project(self):
        # Setup request dict
        request_dict = {"name": "projectName"}

        # Post request on projects
        rv = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                           data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(rv.data.decode())['name'])
        self.assertEqual(201, rv.status_code)

        # Post same request on projects again, should fail
        rv = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                           data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace creation fails
        self.assertEqual(409, rv.status_code)

    def test_get_projects(self):
        request_dict1 = {"name": "projectsGet1"}
        request_dict2 = {"name": "projectsGet2"}

        # Post request on projects
        self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                      data=json.dumps(request_dict1), content_type='application/json')
        self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                      data=json.dumps(request_dict2), content_type='application/json')

        # Post request on projects
        rv = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/')

        result = json.loads(rv.data.decode())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], request_dict1['name'])
        self.assertEqual(result[1]['name'], request_dict2['name'])

    def test_get_project(self):
        request_dict = {"name": "projectGet"}

        # Post request on projects
        rv = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                           data=json.dumps(request_dict), content_type='application/json')
        project_id = json.loads(rv.data.decode())['id']

        # Post request on projects
        rv = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(project_id))

        result = json.loads(rv.data.decode())
        self.assertEqual(200, rv.status_code)
        self.assertEqual(result['name'], request_dict['name'])

    def test_delete_project(self):
        request_dict = {"name": "projectDelete"}

        # Post request on projects
        rv = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                           data=json.dumps(request_dict), content_type='application/json')
        project_id = json.loads(rv.data.decode())['id']

        # Post request on projects
        rv = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(project_id))

        result = json.loads(rv.data.decode())
        self.assertEqual(200, rv.status_code)
        self.assertEqual(result['name'], request_dict['name'])

        # check if its really been deleted
        rv = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(project_id))
        self.assertEqual(404, rv.status_code)
