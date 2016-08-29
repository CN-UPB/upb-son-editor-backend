import shlex
from flask.globals import request

from son.editor.app.exceptions import NotFound
from son.editor.models.project import Project
from son.editor.models.service import Service
from son.editor.app.database import db_session
from son.editor.app.util import getJSON


def get_services(wsID, parentID):
    session = db_session()
    project = session.query(Project).filter_by(id=parentID).first()
    session.commit()
    if project:
        return list(map(lambda x: x.as_dict(), project.services))
    else:
        raise NotFound("No project matching id {}".format(parentID))


def create_service(wsID, parentID):
    session = db_session()
    service_data = getJSON(request)
    project = session.query(Project).filter_by(id=parentID).first()

    if project:
        # Retrieve post parameters
        service_name = shlex.quote(service_data["name"])
        vendor_name = shlex.quote(service_data["vendor"])
        version = shlex.quote(service_data["version"])

        # Create db object
        service = Service(name=service_name, vendor=vendor_name, version=version)

        session.add(service)
        project.services.append(service)
        session.commit()
        return service.as_dict()
    else:
        raise NotFound("Project with id '{}‘ not found".format(parentID))


def update_service(wsID, parentID, serviceID):
    session = db_session()
    service_data = getJSON(request)
    service = session.query(Service).filter_by(id=serviceID).first()
    if service:
        # Parse parameters and update record
        service_name = shlex.quote(service_data["name"])
        vendor_name = shlex.quote(service_data["vendor"])
        version = shlex.quote(service_data["version"])
        if service_name:
            service.name = service_name
        if vendor_name:
            service.vendor = vendor_name
        if version:
            service.version = version
        session.commit()
        return service.as_dict()
    else:
        raise NotFound("Could not update service '{}', because no record was found".format(serviceID))


def delete_service(parentID, serviceID):
    session = db_session()
    project = session.query(Project).filter(Project.id == parentID).first()
    service = session.query(Service).filter(Service.id == serviceID).first()

    if project:
        if service in project.services:
            project.services.remove(service)
        if service:
            session.delete(service)
            session.commit()
        else:
            raise NotFound("Delete service did not work, service with id {} not found".format(serviceID))
    else:
        raise NotFound("Delete service did not work, project with id {} not found".format(serviceID))
