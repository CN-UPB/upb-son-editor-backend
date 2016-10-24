import json
import unittest

from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.util import constants
from son_editor.util.context import init_test_context
from son_editor.tests.utils import *


class ServiceAPITest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        self.user = create_logged_in_user(self.app, 'user_b')
        # Create a workspace and project
        self.wsid = create_workspace(self.user, 'WorkspaceA')
        self.pid = create_project(self.wsid, 'ProjectA')
        self.sid = create_ns(self.wsid, self.pid, "ServiceA", "de.upb.cs.cn.pgsandman", "0.0.1")

    def test_create_service(self):
        session = db_session()

        session.commit()

        postArg = json.dumps({"vendor": "de.upb.cs.cn.pgsandman",
                              "name": "Service Name",
                              "version": "0.0.1"})
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pid)
                                 + "/" + constants.SERVICES + "/", headers={'Content-Type': 'application/json'},
                                 data=postArg)
        self.assertEqual(response.status_code, 201)

        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/", headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)

    def test_get_services(self):
        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/")

        services = json.loads(response.data.decode())
        self.assertEqual(len(services), 2)
        self.assertEqual(services[1]['vendor'], "de.upb.cs.cn.pgsandman")

        self.assertEqual(response.status_code, 200)

    def test_update_service(self):
        # test partial update
        postArg = json.dumps({"name": "New Service Name"})
        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/" + str(self.sid),
                                headers={'Content-Type': 'application/json'},
                                data=postArg)
        service = json.loads(response.data.decode())
        self.assertEqual(service['name'], "'New Service Name'")

        # test complete update
        postArg = json.dumps({"vendor": "de.upb.cs",
                              "name": "Service Name",
                              "version": "1.0"})

        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/" + str(self.sid),
                                headers={'Content-Type': 'application/json'},
                                data=postArg)
        service = json.loads(response.data.decode())
        self.assertEqual(service['vendor'], "de.upb.cs")
        self.assertEqual(service['name'], "'Service Name'")
        self.assertEqual(service['version'], "1.0")

    def test_delete_exists_service(self):
        # delete existing
        response = self.app.delete("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                   + "/" + constants.PROJECTS + "/" + str(self.pid)
                                   + "/" + constants.SERVICES + "/" + str(self.sid),
                                   headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)

    def test_delete_non_exists_service(self):
        # delete non existing
        response = self.app.delete("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                   + "/" + constants.PROJECTS + "/" + str(self.pid)
                                   + "/" + constants.SERVICES + "/" + str(1337),
                                   headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 404)
