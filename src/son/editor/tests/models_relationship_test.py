import unittest

from .model_fixture_test import ModelsTestCase


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