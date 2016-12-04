import logging

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound
from son_editor.impl.catalogue_servicesimpl import get_all_in_catalogue
from son_editor.impl.cataloguesimpl import get_catalogues
from son_editor.impl.usermanagement import get_user
from son_editor.models.private_descriptor import PrivateFunction, PrivateService
from son_editor.models.project import Project

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


def query_private_nsfs(vendor, name, version, is_vnf):
    """
    Finds a function in the private catalogue
    :param vendor:
    :param name:
    :param version:
    :return:
    """
    session = db_session()
    if is_vnf:
        descriptor = session.query(PrivateFunction).filter(PrivateFunction.name == name and
                                                           PrivateFunction.vendor == vendor and
                                                           PrivateFunction.version == version and
                                                           PrivateFunction.workspace.owner == get_user(
                                                               session['user_data'])).first()
    else:
        descriptor = session.query(PrivateService).filter(
            PrivateService.name == name and
            PrivateService.vendor == vendor and
            PrivateService.version == version and PrivateFunction.workspace.owner == get_user(
                session['user_data'])).first()
    return descriptor


def find_by_priority(user_data, ws_id, project_id, vendor, name, version, is_vnf):
    """
    Tries to find vnf / network services by descending priority project / private catalogue / public catalogue.
    :param user_data:
    :param ws_id:
    :param project_id:
    :param vendor:
    :param name:
    :param version:
    :param is_vnf:
    :return:
    """
    # 1. Try to find in project
    project = get_project(project_id)
    if project is None:
        raise NotFound("No project with id {} found.".format(project_id))

    function = get_function(project.functions, vendor, name, version) if is_vnf else get_function(project.services,
                                                                                                  vendor, name, version)

    if function is not None:
        return function.as_dict()

    # 2. Try to find in private catalogue
    # private catalogue funcs/nss are cached in db
    function = query_private_nsfs(vendor, name, version, is_vnf)
    if function is not None:
        return function.as_dict()

    # 3. Try to find in public catalogue
    catalogues = get_catalogues(ws_id)
    for catalogue in catalogues:
        try:
            function_list = get_all_in_catalogue(user_data, ws_id, catalogue['id'], is_vnf)
        except:
            continue
        for func in function_list:
            if func['vendor'] == vendor and func['name'] == name and func['version'] == version:
                function = func
                return function.as_dict()

    # If none found, raise exception
    raise NotFound("VNF" if is_vnf else "NS" + " {}:{}:{} not found".format(vendor, name, version))


def find_network_service(user_data, ws_id, project_id, vendor, name, version):
    """
    Finds a network service in the priority: project / private catalogue / public catalogue
    :param user_data:
    :param ws_id:
    :param project_id:
    :param vendor: Vendor name of the function
    :param name: Name of the function
    :param version: The   version of the function
    :return: If found, it returns the network service
    """
    return find_by_priority(user_data, ws_id, project_id, vendor, name, version, False)


def find_vnf(user_data, ws_id, project_id, vendor, name, version):
    """
    Finds a vnf in the priority: project / private catalogue / public catalogue
    :param user_data:
    :param ws_id:
    :param project_id:
    :param vendor:
    :param name:
    :param version:
    :return:
    """
    return find_by_priority(user_data, ws_id, project_id, vendor, name, version, True)
