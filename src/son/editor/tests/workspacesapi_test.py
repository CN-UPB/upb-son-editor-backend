'''
Created on 26.07.2016

@author: Jonas
'''
import json
import os
import tempfile
import unittest

from son.editor.app import __main__
from son.editor.app.constants import WORKSPACES


class WorkspacesTest(unittest.TestCase):

    def setUp(self):
        self.db_fd, __main__.app.config['DATABASE'] = tempfile.mkstemp()
        __main__.app.config['TESTING'] = True
        self.app = __main__.app.test_client()
        with __main__.app.app_context():
            __main__.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(__main__.app.config['DATABASE'])

    def testCreateWorkSpace(self):
        # when making post requests the '/' at the end seems important, else it defaults to GET oO
        rv = self.app.post('/' + WORKSPACES + '/', data=json.dumps({"name":"workspaceName"}), content_type='application/json', follow_redirects=True)
        print(rv.data)

    def testGetWorkSpaces(self):
        rv = self.app.get('/' + WORKSPACES + '/', follow_redirects=True)
        print(rv.data)

    def testGetWorkSpace(self):
        rv = self.app.get('/' + WORKSPACES + '/wsID', follow_redirects=True)
        print(rv.data)

    def testUpdateWorkSpace(self):
        rv = self.app.put('/' + WORKSPACES + '/wsID', data={"name":"workspaceName"}, follow_redirects=True)
        print(rv.data)

    def testDeleteWorkspace(self):
        rv = self.app.delete('/' + WORKSPACES + '/wsID', follow_redirects=True)
        print(rv.data)


if __name__ == '__main__':
    unittest.main()
