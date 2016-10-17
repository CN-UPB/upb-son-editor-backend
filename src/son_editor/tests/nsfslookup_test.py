import json
import unittest

from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.util import constants
from son_editor.util.context import init_test_context


class NsfslookupTesto(unittest.TestCase):
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
        self.pjid = str(json.loads(response.data.decode())["id"])

        postArg = json.dumps({"vendor": "de.upb.cs.cn.pgsandman",
                              "name": "FunctionA",
                              "version": "0.0.1"})
        response = self.app.post("/" + constants.WORKSPACES + "/" + str(self.wsid)
                                 + "/" + constants.PROJECTS + "/" + str(self.pjid)
                                 + "/" + constants.VNFS + "/", headers=headers,
                                 data=postArg)
        self.fid = str(json.loads(response.data.decode())['id'])

    def tearDown(self):
        session = db_session()
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid + "/" + constants.PROJECTS + "/" + self.pjid)
        self.app.delete("/" + constants.WORKSPACES + "/" + self.wsid)
        session.delete(self.user)
        session.commit()
