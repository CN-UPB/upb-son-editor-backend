import unittest

from son.editor.models.workspace import Workspace
from son.editor.models.project import Project
from son.editor.models.service import Service
from son.editor.models.user import User


class ModelsTestCase(unittest.TestCase):
    # Setup basic stuff
    def setUp(self):
        self.project = Project()
        self.workspace = Workspace()
        self.service = Service()
        self.user = User()


class ModelsRelationshipTest(ModelsTestCase):
    def test_service(self):
        self.service.project = self.project
        self.assertTrue(self.service in self.service.project.services)

    def test_workspace(self):
        self.project.workspace = self.workspace
        self.assertTrue(self.project in self.workspace.projects)

    def test_user(self):
        self.workspace.owner = self.user
        self.assertTrue(self.workspace in self.user.workspaces)