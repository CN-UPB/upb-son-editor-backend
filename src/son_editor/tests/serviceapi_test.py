import json
import unittest

from son_editor.app.database import db_session
from son_editor.models.project import Project
from son_editor.models.service import Service
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util import constants
from son_editor.util.context import init_test_context


class ServiceAPITest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()

        # Add some dummy objects
        self.project = Project(name="Project A")
        self.workspace = Workspace(name="Workspace A")
        self.user = User(name="username", email="foo@bar.com")
        self.service = Service(name="Service a", vendor="de.upb", version="1.0")

        # Add some relationships
        self.workspace.owner = self.user
        self.project.workspace = self.workspace
        self.service.project = self.project

        session = db_session()
        session.add(self.project)
        session.add(self.service)
        session.add(self.workspace)
        session.add(self.user)
        session.commit()
        self.wsid = self.workspace.id
        self.pid = self.project.id
        self.sid = self.service.id

        with self.app as c:
            with c.session_transaction() as session:
                session['userData'] = {'login': 'username'}

    def tearDown(self):
        session = db_session()
        session.delete(self.project)
        session.delete(self.workspace)
        session.delete(self.user)
        session.delete(self.service)
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
        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.workspace.id)
                                + "/" + constants.PROJECTS + "/" + str(self.project.id)
                                + "/" + constants.SERVICES + "/")

        service = json.loads(response.data.decode())
        self.assertEqual(service[0]['vendor'], "de.upb")

        self.assertEqual(response.status_code, 200)

    def test_update_service(self):
        postArg = json.dumps({"vendor": "de.upb.cs",
                              "name": "Service Name",
                              "version": "1.0"})

        response = self.app.put("/" + constants.WORKSPACES + "/" + str(self.workspace.id)
                                + "/" + constants.PROJECTS + "/" + str(self.project.id)
                                + "/" + constants.SERVICES + "/" + str(self.service.id),
                                headers={'Content-Type': 'application/json'},
                                data=postArg)
        service = json.loads(response.data.decode())
        self.assertEqual(service['vendor'], "de.upb.cs")

    def test_delete_exists_service(self):
        # delete existing
        response = self.app.delete("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                   + "/" + constants.PROJECTS + "/" + str(self.pid)
                                   + "/" + constants.SERVICES + "/" + str(self.sid),
                                   headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 200)

    def test_delete_non_exists_service(self):
        # delete non existing
        response = self.app.delete("/" + constants.WORKSPACES + "/" + str(self.workspace.id)
                                   + "/" + constants.PROJECTS + "/" + str(self.project.id)
                                   + "/" + constants.SERVICES + "/" + str(1337),
                                   headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 404)
