import unittest
import json

from son_editor.tests.utils import *
from son_editor.util.context import init_test_context


class ServiceAPITest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()
        self.user = create_logged_in_user(self.app, 'user_b')
        # Create a workspace and project
        self.wsid = create_workspace(self.user, 'WorkspaceA')
        self.pid = create_project(self.wsid, 'ProjectA')
        self.sid = create_ns(self.wsid, self.pid, "service_a", "de.upb.cs.cn.pgsandman", "0.0.1")

    def test_create_service(self):
        session = db_session()

        session.commit()

        post_arg = get_sample_ns("service_name", "de.upb.cs.cn.pgsandman", "0.0.1")
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pid)
                                 + "/" + constants.SERVICES + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(post_arg))
        self.assertEqual(response.status_code, 201)
        service = json.loads(response.data.decode())
        service_id = service["id"]

        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/" + str(service_id),
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(service, json.loads(response.data.decode()))

        # create invalid service
        invalid_service = get_sample_ns("missing_version", "de.upb.cs.cn.pgsandman", "0.0.1")
        invalid_service['descriptor'].pop("descriptor_version", None)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pid)
                                 + "/" + constants.SERVICES + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(invalid_service))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data.decode())['message'], "'descriptor_version' is a required property")

        # create invalid service
        invalid_service = get_sample_ns("NameFormat", "de.upb.cs.cn.pgsandman", "0.0.1")
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pid)
                                 + "/" + constants.SERVICES + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(invalid_service))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data.decode())['message'],
                         "'NameFormat' does not match '^[a-z0-9\\\\-_.]+$'")

    def test_get_services(self):
        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/")

        services = json.loads(response.data.decode())
        self.assertEqual(len(services), 2)
        self.assertEqual(services[1]['descriptor']['vendor'], "de.upb.cs.cn.pgsandman")

        self.assertEqual(response.status_code, 200)

    def test_update_service(self):
        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/" + str(self.sid),
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200, json.loads(response.data.decode()))
        service = json.loads(response.data.decode())

        # update name
        service['descriptor']['name'] = "new_service_name";
        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/" + str(self.sid),
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(service))
        service = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200, response.data.decode())
        self.assertEqual(service["descriptor"]['name'], "new_service_name")

        # test complete update
        service = get_sample_ns("service_name", "de.upb.cs", "1.0")
        service['meta']["positions"] = [{"vnf_1": {'x': 0, 'y': 1}}]
        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/" + str(self.sid),
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(service))
        self.assertEqual(response.status_code, 200, json.loads(response.data.decode()))
        self.assertEqual(service['descriptor'], json.loads(response.data.decode())['descriptor'])
        self.assertEqual(service['meta'], json.loads(response.data.decode())['meta'])

        # test invalid updates: missing version
        service['descriptor']['name'] = "INVALID NAME"
        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                + "/" + constants.PROJECTS + "/" + str(self.pid)
                                + "/" + constants.SERVICES + "/" + str(self.sid),
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(service))
        self.assertEqual(response.status_code, 400, json.loads(response.data.decode())['message'])

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
