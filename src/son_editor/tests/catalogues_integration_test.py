import json
import unittest

from son_editor.util.constants import WORKSPACES, CATALOGUES, SERVICES, PROJECTS, VNFS
from son_editor.app.database import db_session
from son_editor.models.user import User
from son_editor.models.repository import Repository
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.context import init_test_context, CATALOGUE_INSTANCE_URL


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

        # Create workspace by request
        request_dict = {"name": "workspaceName"}
        response = self.app.post('/' + WORKSPACES + '/', data=json.dumps(request_dict), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.wsid = json.loads(response.data.decode())['id']

        # Create project by request
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + PROJECTS + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.pjid = json.loads(response.data.decode())['id']

        # Create catalogue by request
        request_dict = {"name": "Catalogue_Integration_Test", "url": CATALOGUE_INSTANCE_URL}
        response = self.app.post('/' + WORKSPACES + '/' + str(self.wsid) + '/' + CATALOGUES + '/',
                                 data=json.dumps(request_dict), content_type='application/json')
        self.assertEqual(201, response.status_code)
        self.catalogue_id = json.loads(response.data.decode())['id']

        self.ns_dict = {"vendor": "de.upb.integration_test",
                        "name": "service_1",
                        "version": "0.0.1"}

        self.ns_dict_2 = {"vendor": "de.upb.integration_test",
                          "name": "service_2",
                          "version": "0.0.2"}

    def tearDown(self):
        response = self.app.delete('/' + WORKSPACES + '/' + str(self.wsid))
        self.assertEqual(200, response.status_code)
        db_session.delete(self.user)
        db_session.commit()

    def test_catalogue_service_integration(self):
        self.makeTest(False)

    def test_catalogue_vnf_integration(self):
        self.makeTest(True)

    def makeTest(self, is_vnf):

        if (is_vnf):
            url_function_name = VNFS
        else:
            url_function_name = SERVICES

        # Create a sample function
        ns_dict = self.ns_dict
        session = db_session()
        response = self.app.post("/" + WORKSPACES + "/" + str(self.wsid)
                                 + "/" + PROJECTS + "/" + str(self.pjid)
                                 + "/" + url_function_name + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(ns_dict))
        function = json.loads(response.data.decode())
        self.assertTrue(response.status_code == 201)
        self.assertTrue(function['descriptor']['name'] == ns_dict['name'])
        self.assertTrue(function['descriptor']['version'] == ns_dict['version'])
        self.assertTrue(function['descriptor']['vendor'] == ns_dict['vendor'])
        service_id = function['id']

        # Check if ns already in remote catalogue
        response = self.app.get("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                                + "/" + url_function_name + "/")
        functions = json.loads(response.data.decode())
        exists = False
        service_uid = None
        for function in functions:
            if function['vendor'] == ns_dict['vendor'] and function['name'] == ns_dict['name'] and function[
                'version'] == ns_dict['version']:
                service_uid = function['id']
                exists = True

        # Delete existing
        if exists and service_uid is not None:
            self.app.delete("/" + WORKSPACES + "/" + str(self.wsid)
                            + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                            + "/" + url_function_name + "/" + str(service_uid))

        # create ns in remote catalogue
        id_dict = {"id": service_id}

        response = self.app.post("/" + WORKSPACES + "/" + str(self.wsid)
                                 + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                                 + "/" + url_function_name + "/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(id_dict))
        if not exists:
            function = json.loads(response.data)
            service_uid = function['id']
        # retrieve it again
        response = self.app.get("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                                + "/" + url_function_name + "/")
        functions = json.loads(response.data.decode())
        for function in functions:
            if function['vendor'] == ns_dict['vendor'] and function['name'] == ns_dict['name'] and function[
                'version'] == ns_dict['version']:
                exists = True

        self.assertTrue(exists)

        # Check if ns already in remote catalogue
        ns_dict_2 = self.ns_dict_2

        response = self.app.get("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                                + "/" + url_function_name + "/")
        functions = json.loads(response.data.decode())
        exists = False
        service_uid_2 = None
        for function in functions:
            if function['vendor'] == ns_dict_2['vendor'] and function['name'] == ns_dict_2['name'] and function[
                'version'] == ns_dict_2['version']:
                service_uid_2 = function['id']
                exists = True

        # Delete existing
        if exists and service_uid_2 is not None:
            self.app.delete("/" + WORKSPACES + "/" + str(self.wsid)
                            + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                            + "/" + url_function_name + "/" + str(service_uid_2))

        # Update it
        response = self.app.put("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                                + "/" + url_function_name + "/" + str(service_uid), data=ns_dict_2)
        for function in functions:
            if function['vendor'] == ns_dict_2['vendor'] and function['name'] == ns_dict_2['name'] and function[
                'version'] == ns_dict_2['version']:
                exists = True
        self.assertTrue(exists)

        # Retrieve specific
        response = self.app.get("/" + WORKSPACES + "/" + str(self.wsid)
                                + "/" + CATALOGUES + "/" + str(self.catalogue_id)
                                + "/" + url_function_name + "/" + str(service_uid_2))
        function = json.loads(response.data.decode())
        self.assertTrue(function['name'] == ns_dict_2['name'])
        self.assertTrue(function['version'] == ns_dict_2['version'])
        self.assertTrue(function['vendor'] == ns_dict_2['vendor'])


        session.close()
