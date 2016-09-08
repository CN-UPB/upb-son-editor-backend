import json
import unittest

from son_editor.app.constants import WORKSPACES, CATALOGUES
from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util.context import init_test_context


class CatalogueTest(unittest.TestCase):
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
        request_dict = {"name": "CatalogueTest"}
        response = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        self.wsid = json.loads(response.data.decode())['id']

        self.workspace = db_session.query(Workspace).filter_by(id=self.wsid).first()
        db_session.commit()
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(response.data.decode())['name'])

    def tearDown(self):
        response = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid))
        db_session.delete(self.user)
        db_session.commit()

    # Create catalogue
    def test_create_catalogue(self):
        # Setup request dict
        request_dict = {"name": "catalogueName", "url":"http://example.com/some/path/"}

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
        request_dict1 = {"name": "cataloguesGet1", "url":"http://example.com/some/path/"}
        request_dict2 = {"name": "cataloguesGet2", "url":"http://example.com/some/path/"}

        # Post request on catalogues
        self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                      data=json.dumps(request_dict1), content_type='application/json')
        self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                      data=json.dumps(request_dict2), content_type='application/json')

        # Post request on catalogues
        response = self.app.get('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/')

        result = json.loads(response.data.decode())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], request_dict1['name'])
        self.assertEqual(result[1]['name'], request_dict2['name'])

    def test_get_catalogue(self):
        request_dict = {"name": "catalogueGet", "url":"http://example.com/some/path/"}

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
        request_dict = {"name": "catalogueDelete", "url":"http://example.com/some/path/"}

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
