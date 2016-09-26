import json
import unittest

from son_editor.util.constants import WORKSPACES, CATALOGUES, VNFS, PROJECTS
from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util.context import init_test_context


class CatalogueServiceTest(unittest.TestCase):
    def setUp(self):
        # Initializes test context
        self.app = init_test_context()

        # Add some session stuff ( need for finding the user's workspace )
        with self.app as c:
            with c.session_transaction() as session:
                session['userData'] = {'login': 'user'}

        # Add some dummy objects
        self.user = User(name="user", email="foo@bar.com")

        # Add some relationships
        db_session.add(self.user)
        db_session.commit()
        # Create real workspace by request
        request_dict = {"name": "CatalogueTest"}
        response = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        self.wsid = json.loads(response.data.decode())['id']

        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + "/" + PROJECTS + "/",
                                 data=json.dumps(request_dict), content_type='application/json')
        self.pjid = json.loads(response.data.decode())['id']

        self.workspace = db_session.query(Workspace).filter_by(id=self.wsid).first()
        db_session.commit()
        # Expect workspace gets created
        self.assertEqual(request_dict['name'], json.loads(response.data.decode())['name'])

    def tearDown(self):
        response = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid))
        db_session.delete(self.user)
        db_session.commit()

    def test_catalogue_integration(self):
        # Create a sample function
        session = db_session()
        ns_dict = {"vendor": "de.upb.cs.cn.pgsandman",
                   "name": "vnf_1",
                   "version": "0.0.1"}
        post_arg = json.dumps(ns_dict)
        response = self.app.post("/" + WORKSPACES + "/" + str(self.wsid)
                                 + "/" + PROJECTS + "/" + str(self.pjid)
                                 + "/" + VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=post_arg)
        function = json.loads(response.data.decode())
        self.assertTrue(response.status_code == 201)
        self.assertTrue(function['descriptor']['name'] == ns_dict['name'])
        self.assertTrue(function['descriptor']['version'] == ns_dict['version'])
        self.assertTrue(function['descriptor']['vendor'] == ns_dict['vendor'])
        vnf_id = function['id']

        concrete_test_url = "http://fg-cn-sandman1.cs.upb.de:4011"

        # Create catalogue in database
        request_dict = {"name": "sandman1", "url": concrete_test_url}
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        self.assertEqual(request_dict['name'], json.loads(response.data.decode())['name'])
        self.assertEqual(201, response.status_code)

        # Save created catalogue id
        catalogue_id = int(json.loads(response.data.decode())['id'])

        # Check if ns already in remote catalogue

        response = self.app.get("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(catalogue_id)
                                + "/" + VNFS + "/")
        functions = json.loads(response.data.decode())
        exists = False
        vnf_uid = None
        for function in functions:
            if function['vendor'] == ns_dict['vendor'] and function['name'] == ns_dict['name'] and function[
                'version'] == ns_dict['version']:
                vnf_uid = function['id']
                exists = True

        # Delete existing
        if exists and vnf_uid is not None:
            self.app.delete("/" + WORKSPACES + "/" + str(self.wsid)
                            + "/" + CATALOGUES + "/" + str(catalogue_id)
                            + "/" + VNFS + "/" + str(vnf_uid))

        # create ns in remote catalogue
        id_dict = {"id": vnf_id}

        post_arg = json.dumps(id_dict)
        response = self.app.post("/" + WORKSPACES + "/" + str(self.wsid)
                                 + "/" + CATALOGUES + "/" + str(catalogue_id)
                                 + "/" + VNFS + "/", headers={'Content-Type': 'application/json'},
                                 data=post_arg)

        # retrieve it again
        response = self.app.get("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(catalogue_id)
                                + "/" + VNFS + "/")
        functions = json.loads(response.data.decode())
        for function in functions:
            if function['vendor'] == ns_dict['vendor'] and function['name'] == ns_dict['name'] and function[
                'version'] == ns_dict['version']:
                exists = True

        self.assertTrue(exists)

        # Check if ns already in remote catalogue
        ns_dict = {"vendor": "de.upb.cs.cn.pgsandman",
                   "name": "vnf_2",
                   "version": "0.0.2"}

        response = self.app.get("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(catalogue_id)
                                + "/" + VNFS + "/")
        functions = json.loads(response.data.decode())
        exists = False
        vnf_uid_2 = None
        for function in functions:
            if function['vendor'] == ns_dict['vendor'] and function['name'] == ns_dict['name'] and function[
                'version'] == ns_dict['version']:
                vnf_uid_2 = function['id']
                exists = True

        # Delete existing
        if exists and vnf_uid_2 is not None:
            self.app.delete("/" + WORKSPACES + "/" + str(self.wsid)
                            + "/" + CATALOGUES + "/" + str(catalogue_id)
                            + "/" + VNFS + "/" + str(vnf_uid_2))

        # Update it
        response = self.app.put("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(catalogue_id)
                                + "/" + VNFS + "/" + str(vnf_uid), data=ns_dict)
        for function in functions:
            if function['vendor'] == ns_dict['vendor'] and function['name'] == ns_dict['name'] and function[
                'version'] == ns_dict['version']:
                exists = True
        self.assertTrue(exists)

        session.close()
