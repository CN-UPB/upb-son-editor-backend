import json
import unittest

from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.util import constants
from son_editor.util.context import init_test_context


class ServiceAPITest(unittest.TestCase):
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
        self.pid = str(json.loads(response.data.decode())["id"])

        postArg = json.dumps({"vendor": "de.upb.cs.cn.pgsandman",
                              "name": "ServiceA",
                              "version": "0.0.1"})
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pid)
                                 + "/" + constants.SERVICES + "/", headers=headers,
                                 data=postArg)
        self.sid = str(json.loads(response.data.decode())['id'])

    def tearDown(self):
        session = db_session()
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.PROJECTS + "/" + self.pid)
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid)
        session.delete(self.user)
        session.commit()

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
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['vendor'], "de.upb.cs.cn.pgsandman")

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
