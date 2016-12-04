import unittest
import json

from son_editor.tests.utils import *
from son_editor.util import constants
from son_editor.util.context import init_test_context


class FunctionTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Add some session stuff ( need for finding the user's workspace )
        self.user = create_logged_in_user(self.app, 'username')
        # Create a workspace and project
        self.wsid = str(create_workspace(self.user, 'WorkspaceA'))
        self.pjid = str(create_project(self.wsid, 'ProjectA'))
        self.fid = create_vnf(self.wsid, self.pjid, "function_a", "de.upb.cs.cn.pgsandman", "0.0.1")

    def tearDown(self):
        session = db_session()
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.PROJECTS + "/" + self.pjid)
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid)
        session.delete(self.user)
        session.commit()

    def test_create_function(self):
        post_arg = get_sample_vnf("vnf_1", "de.upb.cs.cn.pgsandman", "0.0.1")
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(post_arg))
        self.assertEqual(response.status_code, 201, json.loads(response.data.decode()))
        function = json.loads(response.data.decode())
        self.assertTrue(function['descriptor'], post_arg)

        post_arg = get_sample_vnf("invalid name", "de.upb.cs.cn.pgsandman", "0.0.1")
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(post_arg))
        self.assertEqual(response.status_code, 400, json.loads(response.data.decode()))

        # create invalid vnf: missing vendor
        post_arg = get_sample_vnf("name", "de.upb.cs.cn.pgsandman", "0.0.1")
        post_arg.pop("vendor", None)  # remove vendor
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(post_arg))
        self.assertEqual(response.status_code, 400, json.loads(response.data.decode()))

    def test_get_specific_function(self):
        session = db_session()
        dict = get_sample_vnf("vnf_3", "de.upb.cs.cn.pgsandman", "0.0.1")
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
        dict = get_sample_vnf("vnf_2", "de.upb.cs.cn.pgsandman", "0.0.1")
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
        self.assertEqual(len(functions), 3)
        result = functions[2]
        self.assertEqual(result['descriptor']['name'], dict['name'])
        self.assertTrue(result['descriptor']['version'] == dict['version'])
        self.assertTrue(result['descriptor']['vendor'] == dict['vendor'])

    def test_update_function(self):
        # put vnf in table
        result_id = create_vnf(self.wsid, self.pjid, "vnf_2", "de.upb.cs.cn.pgsandman", "0.0.1")
        update_dict = get_sample_vnf("vnf_3", "de.upb.cs.cn.pgsandman1", "0.0.2")
        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                + "/" + constants.VNFS + "/" + str(result_id),
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(update_dict))
        result = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200, result)
        self.assertEqual(result['descriptor'], update_dict)

        # test invalid function update
        update_dict = get_sample_vnf("vnf_ 3", "de.upb.cs.cn.pgsandman1", "0.0.2")
        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                + "/" + constants.VNFS + "/" + str(result['id']),
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(update_dict))
        result = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400, result)

    def test_delete_function(self):
        # put vnf in table
        dict = get_sample_vnf("vnf_2", "de.upb.cs.cn.pgsandman", "0.0.1")
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
