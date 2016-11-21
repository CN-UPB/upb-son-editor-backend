import json
import os
from unittest import TestCase

import pkg_resources

from son_editor.app.database import db_session
from son_editor.app.exceptions import PackException, ExtNotReachable
from son_editor.models.project import Project
from son_editor.models.repository import Platform
from son_editor.models.user import User
from son_editor.util import publishutil
from son_editor.util.constants import WORKSPACES, PROJECTS, SERVICES
from son_editor.util.context import init_test_context
from son_editor.tests.utils import *


class TestPublishutil(TestCase):
    def setUp(self):
        self.test_package_location = pkg_resources.resource_filename(__name__, "test.son")
        self.app = init_test_context()
        self.user = create_logged_in_user(self.app, 'username')
        self.wsid = str(create_workspace(self.user, 'workspaceName'))
        self.pjid = create_project(self.wsid, 'project_name')
        self.pjid2 = create_project(self.wsid, 'InvalidProjectName')

    def tearDown(self):
        self.app.delete('/' + WORKSPACES + '/' + self.wsid)
        session = db_session()
        session.delete(self.user)
        session.commit()

    def test_pack_project(self):
        session = db_session()
        project = session.query(Project).filter(Project.id == self.pjid).first()
        package_path = publishutil.pack_project(project)

        self.assertTrue(os.path.exists(package_path))
        self.assertTrue(os.path.isfile(package_path))

        # create another service in project
        request_dict = {'descriptor': {"name": "servicename",
                                       "vendor": "vendorname",
                                       "version": "0.1",
                                       "descriptor_version": "0.1"},
                        'meta': {}}
        response = self.app.post(
            '/' + WORKSPACES + '/' + self.wsid + '/' + PROJECTS + '/' + str(self.pjid) + '/' + SERVICES + '/',
            data=json.dumps(request_dict),
            content_type='application/json')

        # should fail because the project name is invalid
        project = session.query(Project).filter(Project.id == self.pjid).first()
        try:
            publishutil.pack_project(project)
        except Exception as err:
            self.assertTrue(isinstance(err, PackException))

            # should fail as only one service can be packaged
            project = session.query(Project).filter(Project.id == self.pjid2).first()
            try:
                publishutil.pack_project(project)
            except Exception as err:
                self.assertTrue(isinstance(err, PackException))

        session.commit()

    def test_push_project(self):
        package_path = self.test_package_location
        result = publishutil.push_to_platform(package_path=package_path,
                                              platform=Platform(url="http://fg-cn-sandman2.cs.upb.de:1234"))
        self.assertTrue(result)
        caught = False
        try:
            result = publishutil.push_to_platform(package_path=package_path,
                                                  platform=Platform(
                                                      url="http://fg-cn-sandman2.cs.upb.de:1010"))  # wrong port
        except ExtNotReachable:
            caught = True
        self.assertTrue(caught)
