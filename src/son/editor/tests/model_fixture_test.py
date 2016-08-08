import unittest

from son.editor.models.workspace import Workspace
from son.editor.models.project import Project
from son.editor.models.service import Service
from son.editor.models.user import User


class ModelsTestCase(unittest.TestCase):
    # Setup basic stuff
    def setUp(self):
        self.project = Project(name="Project A")
        self.workspace = Workspace(name="Workspace A")
        self.service = Service(name="Service A")
        self.user = User(name="User A")

    def test(self):
        self.assertTrue(self,False)