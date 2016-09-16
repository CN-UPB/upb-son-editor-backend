import json
import unittest

from son_editor.app.database import db_session
from son_editor.models.project import Project
from son_editor.models.service import Service
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util import constants
from son_editor.util.context import init_test_context


class FunctionTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Add some session stuff ( need for finding the user's workspace )
        with self.app as c:
            with c.session_transaction() as session:
                session['userData'] = {'login': 'username'}

        self.user = User(name="username", email="foo@bar.com")
        session = db_session()
        session.add(self.user)
        session.commit()

        # Create a workspace and project
        headers = {'Content-Type': 'application/json'}
        response = self.app.post("/" + constants.WORKSPACES + "/",
                                 headers=headers,
                                 data=json.dumps({'name': 'WorkspaceA'}))
        self.wsid = str(json.loads(response.data.decode())["id"])
        response = self.app.post("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.PROJECTS + "/",
                                 headers=headers,
                                 data=json.dumps({'name': 'ProjectA'}))
        self.pjid = str(json.loads(response.data.decode())["id"])

        postArg = json.dumps({"vendor": "de.upb.cs.cn.pgsandman",
                              "name": "FunctionA",
                              "version": "0.0.1"})
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers=headers,
                                 data=postArg)
        self.fid = str(json.loads(response.data.decode())['id'])

    def tearDown(self):
        session = db_session()
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.PROJECTS + "/" + self.pjid)
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid)
        session.delete(self.user)
        session.commit()

    def test_create_function(self):
        session = db_session()
        dict = {"vendor": "de.upb.cs.cn.pgsandman",
                "name": "vnf_1",
                "version": "0.0.1"}
        post_arg = json.dumps(dict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=post_arg)
        function = json.loads(response.data.decode())
        self.assertTrue(response.status_code == 201)
        self.assertTrue(function['descriptor']['name'] == dict['name'])
        self.assertTrue(function['descriptor']['version'] == dict['version'])
        self.assertTrue(function['descriptor']['vendor'] == dict['vendor'])
        session.close()

    def test_get_specific_function(self):
        session = db_session()
        dict = {"vendor": "de.upb.cs.cn.pgsandman",
                "name": "vnf_3",
                "version": "0.0.1"}
        post_arg = json.dumps(dict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=post_arg)
        function1 = json.loads(response.data.decode())
        svcid = function1['id']
        self.assertTrue(response.status_code == 201)

        # retrieve it in table
        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                + "/" + constants.VNFS + "/" + str(svcid))
        function = json.loads(response.data.decode())
        self.assertTrue(function['descriptor']['name'] == dict['name'])
        self.assertTrue(function['descriptor']['version'] == dict['version'])
        self.assertTrue(function['descriptor']['vendor'] == dict['vendor'])

    def test_get_function(self):
        # put vnf in table
        dict = {"vendor": "de.upb.cs.cn.pgsandman",
                "name": "vnf_2",
                "version": "0.0.1"}
        postArg = json.dumps(dict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=postArg)

        # retrieve it in table
        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                + "/" + constants.VNFS + "/")
        functions = json.loads(response.data.decode())
        result = functions[1]
        self.assertEqual(result['descriptor']['name'],dict['name'])
        self.assertTrue(result['descriptor']['version'] == dict['version'])
        self.assertTrue(result['descriptor']['vendor'] == dict['vendor'])

    def test_update_function(self):
        # put vnf in table
        dict = {"vendor": "de.upb.cs.cn.pgsandman",
                "name": "vnf_2",
                "version": "0.0.1"}
        postArg = json.dumps(dict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=postArg)
        js = json.loads(response.data.decode())
        self.assertEqual(js['descriptor'], dict)
        updateDict = {"vendor": "de.upb.cs.cn.pgsandman1",
                      "name": "vnf_3",
                      "version": "0.0.2"}
        updateArg = json.dumps(updateDict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=updateArg)
        result = json.loads(response.data.decode())
        self.assertTrue(result['descriptor']['name'] == updateDict['name'])
        self.assertTrue(result['descriptor']['version'] == updateDict['version'])
        self.assertTrue(result['descriptor']['vendor'] == updateDict['vendor'])

    def test_delete_function(self):
        # put vnf in table
        dict = {"vendor": "de.upb.cs.cn.pgsandman",
                "name": "vnf_2",
                "version": "0.0.1"}
        postArg = json.dumps(dict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=postArg)

        retVal = json.loads(response.data.decode())

        response = self.app.delete("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                   + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                   + "/" + constants.VNFS + "/" + str(retVal['id']),
                                   headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
