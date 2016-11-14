import json
import unittest

from son_editor.app.database import db_session, reset_db, scan_workspaces_dir, _scan_private_catalogue
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util.constants import WORKSPACES, PROJECTS
from son_editor.util.context import init_test_context
from son_editor.tests.utils import *
import os


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

    def test_scan_private_catalogue(self):
        # Create dummy in private catalogue
        session = db_session()
        ws = session.query(Workspace).filter(Workspace.id == self.wsid).first()
        path = ws.path + "/catalogues/ns_catalogue/vendor_test/name_test/version_test/"
        os.makedirs(path)
        file = open(path + "descriptor.yml", 'a')
        file.write('vendor: "son-editor"\n' +
                   'name: "test"\n' +
                   'version: "0.2"')
        file.close()
        _scan_private_catalogue(ws.path + "/catalogues/")
