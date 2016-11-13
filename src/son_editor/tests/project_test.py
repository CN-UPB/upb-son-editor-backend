import unittest
import json

from son_editor.tests.utils import *
from son_editor.util.constants import WORKSPACES, PROJECTS
from son_editor.util.context import init_test_context


class ProjectTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        self.user = create_logged_in_user(self.app, "user_a")
        # Create real workspace by request
        self.wsid = create_workspace(self.user, 'ProjectTest')

    # Create project
    def test_create_project(self):
        # Setup request dict
        request_dict = {"name": "projectName"}

        # Post request on projects
        rv = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                           data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace gets created
        self.assertEqual(201, rv.status_code)
        result_dict = json.loads(rv.data.decode())
        self.assertEqual(request_dict['name'], result_dict['name'])
        self.assertEqual(["personal"], result_dict['publish_to'])

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

    def test_update_project(self):
        # Setup request dict
        pj_id = create_project(self.wsid, "update_project_name")
        create_project(self.wsid, "another_project_name")

        request_dict = {"name": "new_project_name", "publish_to": ["cat2"]}

        # Post request on projects
        rv = self.app.put('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(pj_id),
                          data=json.dumps(request_dict), content_type='application/json')
        # Expect project gets updated
        self.assertEqual(200, rv.status_code)
        result_dict = json.loads(rv.data.decode())
        self.assertEqual(request_dict['name'], result_dict['name'])
        self.assertEqual(["cat2"], result_dict['publish_to'])

        request_dict = {"name": "another_project_name", "publish_to": ["cat2"]}
        # update to existing name, should fail
        rv = self.app.put('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(pj_id),
                          data=json.dumps(request_dict), content_type='application/json')
        # Expect project update fails
        self.assertEqual(409, rv.status_code)
