import unittest


from son.editor.models.workspace import Workspace
from son.editor.models.project import Project
from son.editor.models.service import Service
from son.editor.models.user import User


class ModelsRelationshipTest(unittest.TestCase):
    def setUp(self):
        self.project = Project(name="Project A")
        self.workspace = Workspace(name="Workspace A")
        self.service = Service(name="Service A")
        self.user = User(name="User A")

    def test_service(self):
        self.service.project = self.project
        self.assertTrue(self.service in self.service.project.services)

    def test_workspace(self):
        self.project.workspace = self.workspace
        self.assertTrue(self.project in self.workspace.projects)

    def test_user(self):
        self.workspace.owner = self.user
        self.assertTrue(self.workspace in self.user.workspaces)
