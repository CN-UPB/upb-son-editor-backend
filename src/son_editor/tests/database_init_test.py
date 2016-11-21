import os
import unittest

from son_editor.app.database import reset_db, scan_workspaces_dir, _scan_private_catalogue
from son_editor.models.workspace import Workspace
from son_editor.tests.utils import *
from son_editor.util.context import init_test_context


class ProjectTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Add user
        self.user = create_logged_in_user(self.app, 'user')
        # Create real workspace by request
        self.wsid = create_workspace(self.user, "test_ws")
        create_project(self.wsid, "test_pj")

    @staticmethod
    def test_scan_workspace():
        reset_db()
        scan_workspaces_dir()

    @staticmethod
    def create_catalogue_descriptor(ws: Workspace, vendor: str, name: str, version: str, isVNF: bool):
        catalogueType = "vnf_catalogue" if isVNF else "ns_catalogue"
        path = ws.path + "/catalogues/{}/{}/{}/{}/".format(catalogueType, vendor, name, version)
        os.makedirs(path)
        file = open(path + "descriptor.yml", 'a')
        file.write('vendor: "{}"\n'.format(vendor) +
                   'name: "{}"\n'.format(name) +
                   'version: "{}"'.format(version))
        file.close()

    def test_scan_private_catalogue(self):
        from son_editor.models.private_descriptor import PrivateFunction, PrivateService

        session = db_session()
        ws = session.query(Workspace).filter(Workspace.id == self.wsid).first()

        # Create an ns
        ns_vendor = 'son-editor'
        ns_name = 'test-ns'
        ns_version = '0.1'
        ns_uid = '{}:{}:{}'.format(ns_vendor, ns_name, ns_version)

        # Create dummy network service with descriptor
        ProjectTest.create_catalogue_descriptor(ws, ns_vendor, ns_name, ns_version, False)

        # Create a vnf
        vnf_vendor = 'son-editor'
        vnf_name = 'test-vnf'
        vnf_version = '0.1'
        vnf_uid = '{}:{}:{}'.format(vnf_vendor, vnf_name, vnf_version)

        # Create dummy vnf with descriptor
        ProjectTest.create_catalogue_descriptor(ws, vnf_vendor, vnf_name, vnf_version, True)

        # Scan the private catalogue
        _scan_private_catalogue(ws.path + "/catalogues/")
        result_ns = session.query(PrivateService).filter(PrivateService.uid == ns_uid)[0]
        self.assertTrue(result_ns.name == ns_name and result_ns.vendor == ns_vendor, result_ns.version == ns_version)

        result_vnf = session.query(PrivateFunction).filter(PrivateFunction.uid == vnf_uid)[0]
        self.assertTrue(result_vnf.name == vnf_name and result_vnf.vendor == vnf_vendor,
                        result_vnf.version == vnf_version)
