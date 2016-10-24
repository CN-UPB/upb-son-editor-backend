import unittest

from son_editor.tests.utils import *
from son_editor.util.context import init_test_context


class NsfslookupTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        # Create login
        self.user = create_logged_in_user(self.app, "user_a")

        self.wsid = create_workspace(self, "workspace_a")
        self.pjid = create_project(self, self.wsid, "project_a")
        self.vnfid = create_vnf(self, self.wsid, self.pjid, "virtual_function_a", "de.upb.cs.cn.pgsandman", "0.0.1")
        self.nsid = create_ns(self, self.wsid, self.pjid, "network_service_a", "de.upb.cs.cn.pgsandman",
                              "0.0.1")

    def tearDown(self):
        session = db_session()
        delete_workspace(self, self.wsid)
        session.delete(self.user)
        session.commit()
