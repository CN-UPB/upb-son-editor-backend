from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound
from son_editor.models.project import Project
import son.editor.app.exceptions
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
    """ Finds a function in the given set of functions which matches vendor,name,version """
    for function in functions:
        if function.name == name and function.vendor == vendor and function.version == version:
            return function
    return None


def find_network_service(user_data, ws_id, project_id, vendor, name, version):
    """Finds a network service in the priority: project / private catalogue / public catalogue"""
    session = db_session()
    project = get_project(project_id)

    # Look at project services
    service = get_function(project.services)

    if service is None:
        raise NotFound("No service {}:{}:{} found")

    return None


def find_vnf(user_data, ws_id, project_id, vendor, name, version):
    """Finds a vnf in the priority: project / private catalogue / public catalogue"""
    session = db_session()
    project = get_project(project_id)

    function = get_function(project.functions)

    if function is None:
        raise NotFound("No vnf {}:{}:{} found")

    return None
