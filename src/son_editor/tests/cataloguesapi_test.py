import json
import unittest

from son_editor.util.constants import WORKSPACES, CATALOGUES, VNFS
from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util.context import init_test_context
from son_editor.tests.utils import *


class CatalogueTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()

        # Add some session stuff ( need for finding the user's workspace )
        self.user = create_logged_in_user(self.app, 'user')

        # Create real workspace by request
        self.wsid = create_workspace(self.user, 'CatalogueTest')
    # Create catalogue
    def test_create_catalogue(self):
        # Setup request dict
        request_dict = {"name": "catalogueName", "url": "http://example.com/some/path/"}

        # Post request on catalogues
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(response.data.decode())['name'])
        self.assertEqual(201, response.status_code)

        # Post same request on catalogues again, should fail
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace creation fails
        self.assertEqual(409, response.status_code)

    def test_get_catalogues(self):
        # retreive sample catalogues
        response = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/')

        result = json.loads(response.data.decode())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "cat1")
        self.assertEqual(result[1]['name'], "cat2")

    def test_get_catalogue(self):
        request_dict = {"name": "catalogueGet", "url": "http://example.com/some/path/"}

        # Post request on catalogues
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        catalogue_id = json.loads(response.data.decode())['id']

        # Post request on catalogues
        response = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/' + str(catalogue_id))

        result = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(result['name'], request_dict['name'])

    def test_delete_catalogue(self):
        request_dict = {"name": "catalogueDelete", "url": "http://example.com/some/path/"}

        # Post request on catalogues
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        catalogue_id = json.loads(response.data.decode())['id']

        # Post request on catalogues
        response = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/' + str(catalogue_id))

        result = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(result['name'], request_dict['name'])

        # check if its really been deleted
        response = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/' + str(catalogue_id))
        self.assertEqual(404, response.status_code)
