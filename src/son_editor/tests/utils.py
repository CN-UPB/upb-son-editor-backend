from son_editor.util import constants
from son_editor.app.exceptions import NameConflict
from son_editor.impl.workspaceimpl import create_workspace
import json


def _get_header():
    return {'Content-Type': 'application/json'}


def create_vnf(testcase, wsid: int, pjid: int, name: str, vendor: str, version: str) -> str:
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

    # Create a virtual network function
    argument = json.dumps({"vendor": vendor,
                           "name": name,
                           "version": version})
    response = testcase.app.post("/" + constants.WORKSPACES + "/" + str(wsid)
                                 + "/" + constants.PROJECTS + "/" + str(pjid)
                                 + "/" + constants.VNFS + "/", headers=_get_header(),
                                 data=argument)
    return str(json.loads(response.data.decode())['id'])


def create_ns(testcase, wsid: int, pjid: int, name: str, vendor: str, version: str) -> int:
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
    response = testcase.app.post("/" + constants.WORKSPACES + "/" + str(wsid)
                                 + "/" + constants.PROJECTS + "/" + str(pjid)
                                 + "/" + constants.SERVICES + "/", headers=_get_header(),
                                 data=json.dumps({"vendor": vendor,
                                                  "name": name,
                                                  "version": version}))
    return str(json.loads(response.data.decode())['id'])


def create_workspace(testcase, ws_name: str) -> int:
    """
    Creates a workspace
    :param testcase: Testcase instance to call HTTP requests
    :param name: Name of the workspace that gets created
    :return: ID of the created workspace
    """

    workspace_data = create_workspace()
    return workspace_data['id']


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


def create_project(testcase, ws_id: int, project_name: str) -> str:
    """
    Creates a project
    :param testcase: Testcase instance to call HTTP requests
    :param ws_id: The workspace where the project gets created
    :param project_name: Name of the workspace that gets created
    :return: ID of the created project
    """
    response = testcase.app.post("/" + constants.WORKSPACES + "/" + str(ws_id) + "/",
                                 headers=_get_header(),
                                 data=json.dumps({'name': project_name}))
    if response.status_code == 409:
        raise NameConflict('Workspace already exists')
    else:
        return int(json.loads(response.data.decode())['id'])
