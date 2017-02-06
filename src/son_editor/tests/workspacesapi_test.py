""""
Created on 26.07.2016

@author: Jonas
"""
import json
import unittest

from son_editor.tests.utils import *
from son_editor.util.constants import WORKSPACES, PROJECTS
from son_editor.util.context import init_test_context


class WorkspacesTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        self.user = create_logged_in_user(self.app, 'user')
        self.workspace = create_workspace(self.user, 'Workspace A')
        self.project = create_project(self.workspace, 'Project A')

    def tearDown(self):
        # deletes all workspaces and other data belonging to this user
        db_session.delete(self.user)
        db_session.commit()

    def test_create_workspace(self):
        request_dict = {"name": "workspaceName"}
        response = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(response.data.decode())['name'])
        self.assertEqual(201, response.status_code)

        request_dict = {"name": "workspaceName"}
        response = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace already exists
        self.assertEqual(409, response.status_code)

    def get_wsid(self):
        response = self.app.get('/' + WORKSPACES + '/')

        # Only one workspace was created beforehand
        return int(json.loads(response.data.decode())[0]['id'])

    def test_get_workspaces(self):
        response = self.app.get('/' + WORKSPACES + '/')
        self.assertEqual(json.loads(response.data.decode())[0]['name'], "'Workspace A'")

    def test_get_workspace(self):
        response = self.app.get('/' + WORKSPACES + '/{}'.format(self.get_wsid()))
        self.assertEqual(json.loads(response.data.decode())['name'], "'Workspace A'")

        # test non existing id
        response = self.app.get('/' + WORKSPACES + '/1337')
        self.assertEqual(404, response.status_code)

    def test_update_workspace(self):
        request_dict = {"name": "workspaceToMove"}
        response = self.app.post('/' + WORKSPACES + '/',
                                 data=json.dumps(request_dict),
                                 content_type='application/json')
        ws_id = json.loads(response.data.decode())['id']

        response = self.app.put('/' + WORKSPACES + '/{}'.format(ws_id), data={"name": "workspaceToMove2"})
        self.assertEqual(json.loads(response.data.decode())['name'], "workspaceToMove2")

        # creating it again with the old name should work
        response = self.app.post('/' + WORKSPACES + '/',
                                 data=json.dumps(request_dict),
                                 content_type='application/json')
        ws_id = json.loads(response.data.decode())['id']

        # renaming again to other name should create a conflict
        response = self.app.put('/' + WORKSPACES + '/{}'.format(ws_id), data={"name": "workspaceToMove2"})
        self.assertEqual(409, response.status_code)

        # try to update non existing
        response = self.app.put('/' + WORKSPACES + '/1337', data={"name": "workspaceToMove2"})
        self.assertEqual(404, response.status_code)

        # try to delete referenced catalogue
        response = json.loads(self.app.post('/' + WORKSPACES + '/', data={"name": "catalogue_ref"}).data.decode())
        ws_id = response["id"]
        cat_name = response["catalogues"][0]['name']
        cat_id = response["catalogues"][0]['id']
        response = self.app.post('/' + WORKSPACES + '/{}'.format(ws_id) + "/" + PROJECTS + "/",
                                 data=json.dumps({"name": "project", "publish_to": [cat_name]}),
                                 content_type='application/json')
        self.assertEqual(201, response.status_code)
        response = self.app.put('/' + WORKSPACES + '/{}'.format(ws_id), data={"name": "catalogue_ref"})
        self.assertEqual(400, response.status_code)

        request_dict = {"name": "catalogue_ref",
                        "catalogues": [
                            {"id": cat_id,
                             "name": "new_name",
                             "url": "http://fg-cn-sandman2.cs.upb.de:4012/"}]}
        response = self.app.put('/' + WORKSPACES + '/{}'.format(ws_id),
                                data=json.dumps(request_dict),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)

        request_dict = {"name": "catalogue_ref",
                        "catalogues": [
                            {"id": cat_id,
                             "name": "new_name",
                             "url": "http://fg-cn-sandman2.cs.upb.de:4011/"}]}  # invalid port
        response = self.app.put('/' + WORKSPACES + '/{}'.format(ws_id),
                                data=json.dumps(request_dict),
                                content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_workspace(self):
        # Create at first a workspace
        request_dict = {"name": "workspaceToDelete"}
        response = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json',
                                 follow_redirects=True)
        ws_id = json.loads(response.data.decode())['id']
        response = self.app.delete('/' + WORKSPACES + '/{}'.format(ws_id))
        self.assertEqual(200, response.status_code)

        # test workspace no longer exists
        response = self.app.get('/' + WORKSPACES + '/')
        workspaces = json.loads(response.data.decode())
        for workspace in workspaces:
            self.assertNotEqual(request_dict['name'], workspace['name'])


if __name__ == '__main__':
    unittest.main()
