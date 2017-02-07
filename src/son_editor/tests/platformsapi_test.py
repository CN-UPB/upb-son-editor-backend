import unittest
import json

from son_editor.tests.utils import *
from son_editor.util.constants import WORKSPACES, PLATFORMS
from son_editor.util.context import init_test_context


class PlatformTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        self.user = create_logged_in_user(self.app, 'user')
        self.wsid = create_workspace(self.user, 'PlatformTest')

    # Create platform
    def test_create_platform(self):
        # Setup request dict
        request_dict = {"name": "platformName", "url": "http://example.com/some/path/"}

        # Post request on platforms
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(response.data.decode())['name'])
        self.assertEqual(201, response.status_code)

        # Post same request on platforms again, should fail
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace creation fails
        self.assertEqual(409, response.status_code)

    def test_get_platforms(self):
        request_dict1 = {"name": "platformsGet1", "url": "http://example.com/some/path/"}
        request_dict2 = {"name": "platformsGet2", "url": "http://example.com/some/path/"}

        # Post request on platforms
        self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/',
                      data=json.dumps(request_dict1), content_type='application/json')
        self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/',
                      data=json.dumps(request_dict2), content_type='application/json')

        # Post request on platforms
        response = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/')

        result = json.loads(response.data.decode())
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1]['name'], request_dict1['name'])
        self.assertEqual(result[2]['name'], request_dict2['name'])

    def test_get_platform(self):
        request_dict = {"name": "platformGet", "url": "http://example.com/some/path/"}

        # Post request on platforms
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        platform_id = json.loads(response.data.decode())['id']

        # Post request on platforms
        response = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/' + str(platform_id))

        result = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(result['name'], request_dict['name'])

    def test_delete_platform(self):
        request_dict = {"name": "platformDelete", "url": "http://example.com/some/path/"}

        # Post request on platforms
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        platform_id = json.loads(response.data.decode())['id']

        # Post request on platforms
        response = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/' + str(platform_id))

        result = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(result['name'], request_dict['name'])

        # check if its really been deleted
        response = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PLATFORMS + '/' + str(platform_id))
        self.assertEqual(404, response.status_code)
