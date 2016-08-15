import unittest
import json

from son.editor.models.workspace import Workspace
from son.editor.models.project import Project
from son.editor.models.user import User

from son.editor.app.database import db_session

from son.editor.app import __main__

from son.editor.app import constants


class ServiceAPITest(unittest.TestCase):
    def setUp(self):
        __main__.app.config['TESTING'] = True
        self.app = __main__.app.test_client()

        # Add some dummy objects
        self.project = Project(name="Project A")
        self.workspace = Workspace(name="Workspace A")
        self.user = User(name="username", email="foo@bar.com")

        # Add some relationships
        self.workspace.owner = self.user;
        self.project.workspace = self.workspace

        db_session.add(self.project)
        db_session.add(self.workspace)
        db_session.add(self.user)
        db_session.commit()

    def tearDown(self):
        db_session.delete(self.project)
        db_session.delete(self.workspace)
        db_session.delete(self.user)
        db_session.commit()

    def test_create(self):
        postArg = json.dumps({"vendor": "de.upb.cs.cn.pgsandman",
                              "name": "Service Name",
                              "version": "0.0.1"})

        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.workspace.id)
                                 + "/" + constants.PROJECTS + "/" + str(self.project.id)
                                 + "/" + constants.SERVICES + "/", headers={'Content-Type': 'application/json'},
                                 data=postArg)
        self.assertTrue(response.status_code == 201)
