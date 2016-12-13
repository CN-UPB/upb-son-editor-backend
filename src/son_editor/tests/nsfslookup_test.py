import unittest
import json

from son_editor.tests.utils import *
from son_editor.util.constants import WORKSPACES, PROJECTS, NSFS, VNFS, SERVICES
from son_editor.util.context import init_test_context
from son_editor.tests.utils import create_private_catalogue_descriptor
from son_editor.app.database import _scan_private_catalogue


class NsfslookupTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Create login
        self.user = create_logged_in_user(self.app, "user_a")

        self.wsid = create_workspace(self.user, "workspace_a")
        self.pjid = create_project(self.wsid, "project_a")
        self.vnf_vendor = "de.upb.cs.cn.pgsandman"
        self.vnf_name = "virtual_function_a"
        self.vnf_version = "0.0.1"
        self.ns_name = "network_service_a"
        self.ns_vendor = "de.upb.cs.cn.pgsandman"
        self.ns_version = "0.0.1"
        self.vnfid = create_vnf(self.wsid, self.pjid, "virtual_function_a", "de.upb.cs.cn.pgsandman", "0.0.1")
        self.nsid = create_ns(self.wsid, self.pjid, self.ns_name, self.ns_vendor,
                              self.ns_version)

    def tearDown(self):
        session = db_session()
        delete_workspace(self, self.wsid)
        session.commit()

    def test_simple_project(self):
        response = self.app.get(
            WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(self.pjid) + '/' +
            NSFS + '/' + VNFS + '/' + self.vnf_vendor + "/" + self.vnf_name + "/" + self.vnf_version)
        response_json = json.loads(response.data.decode())
        self.assertEqual(response_json['descriptor']['vendor'], self.vnf_vendor)
        self.assertEqual(response_json['descriptor']['name'], self.vnf_name)
        self.assertEqual(response_json['descriptor']['version'], self.vnf_version)

        response = self.app.get(
            WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(self.pjid) + '/' +
            NSFS + '/' + SERVICES + '/' + self.ns_vendor + "/" + self.ns_name + "/" + self.ns_version)
        response_json = json.loads(response.data.decode())
        self.assertEqual(response_json['descriptor']['vendor'], self.ns_vendor)
        self.assertEqual(response_json['descriptor']['name'], self.ns_name)
        self.assertEqual(response_json['descriptor']['version'], self.ns_version)

    def test_private_catalogue(self):
        session = db_session()
        vendor = "de.upb"
        name = "private_vnf"
        version = "0.1"

        workspace = session.query(Workspace).filter(Workspace.id == self.wsid)[0]

        create_private_catalogue_descriptor(workspace, vendor, name, version, True)
        _scan_private_catalogue(workspace.path + "/catalogues", workspace)
        response = self.app.get(
            WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/' + str(
                self.pjid) + '/' + NSFS + '/' + VNFS + '/' + vendor + "/" + name + "/" + version)
        response_json = json.loads(response.data.decode())
        self.assertTrue(response_json['vendor'] == vendor and response_json['name'] == name,
                        response_json['version'] == version)
