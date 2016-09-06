import shlex
from flask.globals import request

from son.editor.app.exceptions import NotFound
from son.editor.models.project import Project
from son.editor.models.service import Service
from son.editor.app.database import db_session
from son.editor.app.util import get_json


def get_services(ws_id, parent_id):
    session = db_session()
    project = session.query(Project).filter_by(id=parent_id).first()
    session.commit()
    if project:
        return list(map(lambda x: x.as_dict(), project.services))
    else:
        raise NotFound("No project matching id {}".format(parent_id))


def create_service(ws_id, parent_id):
    session = db_session()
    service_data = get_json(request)
    project = session.query(Project).filter_by(id=parent_id).first()

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
        raise NotFound("Project with id '{}‘ not found".format(parent_id))


def update_service(ws_id, parent_id, service_id):
    session = db_session()
    service_data = get_json(request)
    service = session.query(Service).filter_by(id=service_id).first()
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
        raise NotFound("Could not update service '{}', because no record was found".format(service_id))


def delete_service(parent_id, service_id):
    session = db_session()
    project = session.query(Project).filter(Project.id == parent_id).first()
    service = session.query(Service).filter(Service.id == service_id).first()

    if project:
        if service in project.services:
            project.services.remove(service)
        if service:
            session.delete(service)
            session.commit()
            return service.as_dict()
        else:
            raise NotFound("Delete service did not work, service with id {} not found".format(service_id))
    else:
        raise NotFound("Delete service did not work, project with id {} not found".format(service_id))


def get_service(ws_id, parent_id, service_id):
    session = db_session()
    service = session.query(Service).filter_by(id=service_id).first()
    session.commit()
    if service:
        return service.as_dict()
    else:
        raise NotFound("No Service matching id {}".format(parent_id))
