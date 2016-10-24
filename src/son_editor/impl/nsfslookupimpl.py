from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound
from son_editor.models.project import Project
from son_editor.impl.cataloguesimpl import get_catalogues
from son_editor.impl.catalogue_servicesimpl import get_all_in_catalogue
import logging

logger = logging.getLogger(__name__)


def get_project(project_id):
    """ Retrieves the project which matches the given project id. Otherwise it raises NotFound Exception """
    session = db_session()
    current_project = session.query(Project).filter(Project.id == project_id).first()
    if current_project is not None:
        return current_project
    else:
        raise NotFound("Project {} does not exist".format(project_id))


def get_function(functions, vendor, name, version):
    """
    Finds a function in the given set of functions which matches vendor,name,version
    :param functions: Set of functions to look for the specific one
    :param vendor: Vendor name of the function
    :param name: Name of the function
    :param version: The version of the function
    :return: If found, it returns the function. Otherwise it returns None
    """
    for function in functions:
        if function.name == name and function.vendor == vendor and function.version == version:
            return function
    return None


def findWithPriority(user_data, ws_id, project_id, vendor, name, version, is_vnf):
    # 1. Try to find in project
    project = get_project(project_id)
    if project is None:
        raise NotFound("No project with id {} found.".format(project_id))
    function = None
    if is_vnf:
        function = get_function(project.functions)
    else:
        function = get_function(project.services)

    if function is not None:
        return function

    # 2. Try to find in private catalogue
    # @TODO private catalogue search
    # 3. Try to find in public catalogue
    catalogues = get_catalogues(ws_id)
    function_list = []
    for catalogue in catalogues:
        function_list = get_all_in_catalogue(user_data, ws_id, catalogue.id, is_vnf)
        for func in function_list:
            if func['vendor'] == vendor and func['name'] == name and func['version'] == version:
                pass



def find_network_service(user_data, ws_id, project_id, vendor, name, version):
    """
    Finds a network service in the priority: project / private catalogue / public catalogue
    :param user_data:
    :param ws_id:
    :param project_id:
    :param vendor: Vendor name of the function
    :param name: Name of the function
    :param version: The version of the function
    :return: If found, it returns the network service
    """
    project = get_project(project_id)

    # Look at project services
    service = get_function(project.services)

    if not service:
        catalogues = get_catalogues(ws_id)
        for catalogue in catalogues:
            function_list = get_all_in_catalogue(user_data, ws_id, catalogue.id, 0)
            for function in function_list:
                pass

    if service is None:
        raise NotFound("No service {}:{}:{} found")
    return None


def find_vnf(user_data, ws_id, project_id, vendor, name, version):
    """Finds a vnf in the priority: project / private catalogue / public catalogue"""
    session = db_session()
    project = get_project(project_id)

    function = get_function(project.functions)

    if function is not None:
        # TODO look in private catalogue

        # Public catalogues
        catalogues = get_catalogues(ws_id)
        serviceAndFunctions = []
        for catalogue in catalogues:
            serviceAndFunctions.extend(get_all_in_catalogue(None, ws_id, catalogue.id, 1))

    if function is None:
        raise NotFound("No vnf {}:{}:{} found")

    return None
