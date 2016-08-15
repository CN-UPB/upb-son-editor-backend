'''
Created on 26.07.2016

@author: Jonas
'''
import json
import os
import tempfile
import unittest
import flask

from son.editor.app import __main__
from son.editor.app.constants import WORKSPACES
from son.editor.models.user import User
from son.editor.models.workspace import Workspace
from son.editor.models.project import Project
from son.editor.app.database import db_session
from son.editor.app.util import getJSON


class WorkspacesTest(unittest.TestCase):

    def setUp(self):
        __main__.app.config['TESTING'] = True
        self.app = __main__.app.test_client()

        # Add some dummy objects
        self.project = Project(name="Project A")
        self.workspace = Workspace(name="Workspace A")
        self.user = User(name="user", email="foo@bar.com")

        # Add some relationships
        self.workspace.owner = self.user;
        self.project.workspace = self.workspace

        db_session.add(self.project)
        db_session.add(self.workspace)
        db_session.add(self.user)
        db_session.commit()
        with self.app as c:
            with c.session_transaction() as session:
                session['userData'] = {'login': 'user'}

    def tearDown(self):
        db_session.delete(self.project)
        db_session.delete(self.workspace)
        db_session.delete(self.user)
        db_session.commit()

    def testCreateWorkSpace(self):
        # when making post requests the '/' at the end seems important, else it defaults to GET oO
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps({"name":"workspaceName"}), content_type='application/json', follow_redirects=True)
        # Expect workspace gets created
        self.assertEqual(200,rv.status_code)

    def getWSID(self):
        rv = self.app.get('/' + WORKSPACES + '/', follow_redirects=True)
        return int(json.loads(rv.data.decode())['workspaces'][0]['id'])

    def testGetWorkSpaces(self):
        rv = self.app.get('/' + WORKSPACES + '/', follow_redirects=True)
        print(rv.data)

    def testGetWorkSpace(self):
        rv = self.app.get('/' + WORKSPACES + '/%i' % self.getWSID(), follow_redirects=True)
        print(rv.data)

    def testUpdateWorkSpace(self):
        rv = self.app.put('/' + WORKSPACES + '/%i' % self.getWSID(), data={"name":"workspaceName"}, follow_redirects=True)
        print(rv.data)

    def testDeleteWorkspace(self):
        rv = self.app.delete('/' + WORKSPACES + '/%i' % self.getWSID(), follow_redirects=True)
        print(rv.data)


if __name__ == '__main__':
    unittest.main()
