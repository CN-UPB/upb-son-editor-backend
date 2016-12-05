import son_editor.impl.functionsimpl
import son_editor.impl.projectsimpl
import son_editor.impl.servicesimpl
import son_editor.impl.workspaceimpl
import son_editor.impl.cataloguesimpl
import os
from son_editor.app.database import db_session
from son_editor.impl.usermanagement import get_user
from son_editor.models.user import User
from son_editor.models.workspace import Workspace
from son_editor.util import constants


def _get_header():
    return {'Content-Type': 'application/json'}


def get_sample_vnf(name: str, vendor: str, version: str):
    """
    Creates a minimal valid example vnf from the given name, vendor and version
    :param name: The VNF name
    :param vendor: The VNF vendor
    :param version: The VNF version
    :return: a dictionary with a valid vnf descriptor that will pass validation
    """
    return {
        "vendor": vendor,
        "name": name,
        "version": version,
        "descriptor_version": "0.1",
        "virtual_deployment_units": [
            {
                "id": "vdu_id",
                "resource_requirements": {
                    "cpu": {
                        "vcpus": 1
                    },
                    "memory": {
                        "size": 1
                    }
                }
            }
        ]
    }


def create_vnf(wsid: int, pjid: int, name: str, vendor: str, version: str) -> str:
    """
    Creates a function with given name, vendor and version in the given project returns the id
    :param testcase: Testcase instance to call HTTP requests
    :param wsid: ID of the workspace
    :param pjid: ID of the project
    :param name: Name for the function to create
    :param vendor: Vendor name for the function to create
    :param version: Version name for the function to create
    :returns: ID of the created function
    """
    result = son_editor.impl.functionsimpl.create_function(wsid, pjid, get_sample_vnf(name, vendor, version))
    return result['id']


def get_sample_ns(name: str, vendor: str, version: str) -> dict:
    """
    Creates a minimal valid service descriptor with the given name, vendor and version
    :param name: The name of the service
    :param vendor: the vendor of the service
    :param version: the version of the service
    :return: A dict containing a descriptor that will pass validation and a metadata object for the service
    """
    return {'descriptor': {'name': name,
                           'vendor': vendor,
                           'version': version,
                           "descriptor_version": "0.1"},
            'meta': {'positions': []}}


def create_ns(wsid: int, pjid: int, name: str, vendor: str, version: str) -> int:
    """
    Creates a function with given name, vendor and version in the given project returns the id
    :param wsid: ID of the workspace
    :param pjid: ID of the project
    :param name: Name for the function to create
    :param vendor: Vendor name for the function to create
    :param version: Version name for the function to create
    :returns: ID of the created function
    """

    result = son_editor.impl.servicesimpl.create_service(wsid, pjid, get_sample_ns(name, vendor, version))
    return result['id']


def create_workspace(user: User, ws_name: str) -> int:
    """
    Creates a workspace
    :param user: the user for which to insert the workspace
    :param ws_name: Name of the workspace that gets created
    :return: ID of the created workspace
    """

    ws_data = {'name': ws_name}
    workspace_data = son_editor.impl.workspaceimpl.create_workspace(user.name, ws_data)
    return workspace_data['id']


def create_private_catalogue_descriptor(ws: Workspace, vendor: str, name: str, version: str, isVNF: bool):
    catalogue_type = "vnf_catalogue" if isVNF else "ns_catalogue"
    path = ws.path + "/catalogues/{}/{}/{}/{}/".format(catalogue_type, vendor, name, version)
    os.makedirs(path)
    file = open(path + "descriptor.yml", 'a')
    file.write('vendor: "{}"\n'.format(vendor) +
               'name: "{}"\n'.format(name) +
               'version: "{}"'.format(version))
    file.close()


def create_catalogue(wsid: int, name: str, url: str):
    return son_editor.impl.cataloguesimpl.create_catalogue(wsid, {'name': name, 'url': url})['id']


def create_logged_in_user(app, user_name) -> User:
    """
    Creates a user with database record and session
    :param app: Test context / app
    :param user_name: User name
    :return: Model instance
    """
    # Add some session stuff ( need for finding the user's workspace )
    with app as c:
        with c.session_transaction() as session:
            session['access_token'] = "fake_access_token"
            session['user_data'] = {'login': user_name}

    # Add some dummy objects
    user = User(name=user_name, email=user_name + "@bar.com")
    session = db_session()
    session.add(user)
    session.commit()
    return user


def delete_workspace(testcase, ws_id: int):
    """
    Deletes a workspace
    :param testcase: Testcase instance to call HTTP requests
    :param ws_id: The workspace id which gets deleted
    :return: True, if successful
    """
    response = testcase.app.delete("/" + constants.WORKSPACES + "/" + str(ws_id) + "/",
                                   headers=_get_header())
    return response.status_code == 200


def create_project(ws_id: int, project_name: str) -> str:
    """
    Creates a project
    :param testcase: Testcase instance to call HTTP requests
    :param ws_id: The workspace where the project gets created
    :param project_name: Name of the workspace that gets created
    :return: ID of the created project
    """
    return son_editor.impl.projectsimpl.create_project(ws_id, {'name': project_name})['id']
