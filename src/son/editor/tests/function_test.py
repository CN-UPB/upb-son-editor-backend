import unittest
import json

from son.editor.models.workspace import Workspace
from son.editor.models.project import Project
from son.editor.models.user import User
from son.editor.models.service import Service

from son.editor.app.database import db_session

from son.editor.app import __main__

from son.editor.app import constants


class FunctionTest(unittest.TestCase):
    def setUp(self):
        __main__.app.config['TESTING'] = True
        self.app = __main__.app.test_client()

        # Add some dummy objects
        self.project = Project(name="Project A")
        self.workspace = Workspace(name="Workspace A")
        self.user = User(name="username", email="foo@bar.com")
        self.service = Service(name="Service a", vendor="de.upb", version="1.0")

        # Add some relationships
        self.workspace.owner = self.user;
        self.project.workspace = self.workspace
        self.service.project = self.project

        session = db_session()
        session.add(self.project)
        session.add(self.service)
        session.add(self.workspace)
        session.add(self.user)
        session.commit()
        self.wsid = self.workspace.id
        self.pjid = self.project.id

        # Add some session stuff ( need for finding the user's workspace )
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

    def test_create_function(self):
        session = db_session()
        dict = {"vendor": "de.upb.cs.cn.pgsandman",
                "name": "vnf_1",
                "version": "0.0.1"}
        post_arg = json.dumps(dict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=post_arg)
        function = json.loads(response.data.decode())['created']
        self.assertTrue(response.status_code == 201)
        self.assertTrue(function['descriptor']['name'] == dict['name'])
        self.assertTrue(function['descriptor']['version'] == dict['version'])
        self.assertTrue(function['descriptor']['vendor'] == dict['vendor'])
        session.close()

    def test_get_function(self):
        # put vnf in table
        dict = {"vendor": "de.upb.cs.cn.pgsandman",
                "name": "vnf_2",
                "version": "0.0.1"}
        postArg = json.dumps(dict)
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.workspace.id)
                                 + "/" + constants.PROJECTS + "/" + str(self.project.id)
                                 + "/" + constants.VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=postArg)

        # retrieve it in table
        response = self.app.get("/" + constants.WORKSPACES + "/" + str(self.workspace.id)
                                + "/" + constants.PROJECTS + "/" + str(self.project.id)
                                + "/" + constants.VNFS + "/")
        functions = json.loads(response.data.decode())
        result = functions['functions'][0]
        self.assertTrue(result['descriptor']['name'] == dict['name'])
        self.assertTrue(result['descriptor']['version'] == dict['version'])
        self.assertTrue(result['descriptor']['vendor'] == dict['vendor'])
