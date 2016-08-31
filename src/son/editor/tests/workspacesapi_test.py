'''
Created on 26.07.2016

@author: Jonas
'''
import json
import unittest

from son.editor.app.constants import WORKSPACES
from son.editor.app.database import db_session
from son.editor.models.project import Project
from son.editor.models.user import User
from son.editor.models.workspace import Workspace
from son.editor.util.context import init_test_context


class WorkspacesTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()

        # Add some dummy objects
        self.project = Project(name="Project A")
        self.user = User(name="user", email="foo@bar.com")
        self.workspace = Workspace(name="Workspace A", owner=self.user)

        # Add some relationships

        db_session.add(self.user)
        db_session.add(self.workspace)
        db_session.commit()

        # Add some session stuff ( need for finding the user's workspace )
        with self.app as c:
            with c.session_transaction() as session:
                session['userData'] = {'login': 'user'}

    def tearDown(self):
        db_session.delete(self.user)
        db_session.delete(self.workspace)
        db_session.commit()

    def testCreateWorkSpace(self):
        request_dict = {"name": "workspaceName"}
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(rv.data.decode())['name'])
        self.assertEqual(201, rv.status_code)

    def getWSID(self):
        rv = self.app.get('/' + WORKSPACES + '/')

        # Only one workspace was created beforehand
        return int(json.loads(rv.data.decode())[0]['id'])

    def testGetWorkSpaces(self):
        rv = self.app.get('/' + WORKSPACES + '/')
        self.assertEqual(json.loads(rv.data.decode())[0]['name'], "Workspace A")

    def testGetWorkSpace(self):
        rv = self.app.get('/' + WORKSPACES + '/%i' % self.getWSID())
        self.assertEqual(json.loads(rv.data.decode())['name'], "Workspace A")

    def testUpdateWorkSpace(self):
        request_dict = {"name": "workspaceToMove"}
        rv = self.app.post('/' + WORKSPACES + '/',
                           data=json.dumps(request_dict),
                           content_type='application/json')
        id = json.loads(rv.data.decode())['id']

        rv = self.app.put('/' + WORKSPACES + '/{}'.format(id), data={"name": "workspaceToMove2"},
                          follow_redirects=True)
        self.assertEqual(json.loads(rv.data.decode())['name'], "workspaceToMove2")

    def testDeleteWorkspace(self):
        # Create at first a workspace
        request_dict = {"name": "workspaceToDelete"}
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json',
                           follow_redirects=True)
        id = json.loads(rv.data.decode())['id']
        rv = self.app.delete('/' + WORKSPACES + '/%i' % id)
        self.assertEqual(200, rv.status_code)


if __name__ == '__main__':
    unittest.main()
