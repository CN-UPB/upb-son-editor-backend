import json
import logging
import os
import shlex
import shutil

import jsonschema
from jsonschema import ValidationError
from son.schema.validator import SchemaValidator

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound, NameConflict, InvalidArgument
from son_editor.models.descriptor import Service
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import write_ns_vnf_to_disk, get_file_path, get_schema

logger = logging.getLogger(__name__)


def get_services(ws_id: int, project_id: int) -> list:
    """
    Get a list of all services in this Project
    :param ws_id:
    :param project_id: The project ID
    :return: A list of service descriptors as dicts
    """
    session = db_session()
    project = session.query(Project).filter_by(id=project_id).first()
    session.commit()
    if project:
        return list(map(lambda x: x.as_dict(), project.services))
    else:
        raise NotFound("No project matching id {}".format(project_id))


def create_service(ws_id: int, project_id: int, service_data: dict) -> dict:
    """
    Creates a service in the given project
    :param ws_id: The Workspace of the project
    :param project_id: The Project of the Service
    :param service_data: the service descriptor
    :return: The created service descriptor
    """
    session = db_session()
    project = session.query(Project).filter_by(id=project_id).first()

    if project:
        # Retrieve post parameters
        try:
            service_name = shlex.quote(service_data['descriptor']["name"])
            vendor_name = shlex.quote(service_data['descriptor']["vendor"])
            version = shlex.quote(service_data['descriptor']["version"])
        except KeyError as ke:
            raise InvalidArgument("Missing key {} in service data".format(str(ke)))

        existing_services = list(session.query(Service)
                                 .join(Project)
                                 .join(Workspace)
                                 .filter(Workspace.id == ws_id)
                                 .filter(Service.project == project)
                                 .filter(Service.name == service_name)
                                 .filter(Service.vendor == vendor_name)
                                 .filter(Service.version == version))
        if len(existing_services) > 0:
            raise NameConflict("A service with this name/vendor/version already exists")

        # validate service descriptor
        workspace = session.query(Workspace).filter(Workspace.id == ws_id).first()
        validate_service_descriptor(workspace.path, service_data["descriptor"])

        # Create db object
        service = Service(name=service_name,
                          vendor=vendor_name,
                          version=version,
                          project=project,
                          descriptor=json.dumps(service_data["descriptor"]),
                          meta=json.dumps(service_data["meta"]))
        session.add(service)
        try:
            write_ns_vnf_to_disk("nsd", service)
        except:
            logger.exception("Could not create service:")
            session.rollback()
            raise
        session.commit()
        return service.as_dict()

    else:
        session.rollback()
        raise NotFound("Project with id '{}‘ not found".format(project_id))


def update_service(ws_id, project_id, service_id, service_data):
    """
    Update the service using the service data from the request
    :param ws_id:
    :param project_id:
    :param service_id:
    :param service_data:
    :return:
    """
    session = db_session()
    service = session.query(Service). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == project_id). \
        filter(Service.id == service_id).first()
    if service:
        old_file_name = get_file_path("nsd", service)
        # Parse parameters and update record
        if 'descriptor' in service_data:
            # validate service descriptor
            workspace = session.query(Workspace).filter(Workspace.id == ws_id).first()
            validate_service_descriptor(workspace.path, service_data["descriptor"])
            service.descriptor = json.dumps(service_data["descriptor"])
            try:
                service.name = shlex.quote(service_data["descriptor"]["name"])
                service.vendor = shlex.quote(service_data["descriptor"]["vendor"])
                service.version = shlex.quote(service_data["descriptor"]["version"])
            except KeyError as ke:
                raise InvalidArgument("Missing key {} in function data".format(str(ke)))

        if 'meta' in service_data:
            service.meta = json.dumps(service_data["meta"])

        new_file_name = get_file_path("nsd", service)
        try:
            if not old_file_name == new_file_name:
                shutil.move(old_file_name, new_file_name)
            write_ns_vnf_to_disk("nsd", service)
        except:
            logger.exception("Could not update descriptor file:")
            raise
        session.commit()
        return service.as_dict()
    else:
        raise NotFound("Could not update service '{}', because no record was found".format(service_id))


def delete_service(project_id: int, service_id: int) -> dict:
    """
    Deletes the service from the Database and from the disk
    :param project_id: The Projects ID
    :param service_id: The Services ID
    :return: The descriptor of the deleted service
    """
    session = db_session()
    project = session.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise NotFound("Could not delete service: project with id {} not found".format(service_id))

    service = session.query(Service). \
        filter(Service.id == service_id). \
        filter(Service.project == project). \
        first()
    if service is None:
        raise NotFound("Could not delete service: service with id {} not found".format(service_id))

    session.delete(service)
    try:
        os.remove(get_file_path("nsd", service))
    except:
        session.rollback()
        logger.exception("Could not delete service:")
        raise
    session.commit()
    return service.as_dict()


def get_service(ws_id, parent_id, service_id):
    """
    Get the service by ID
    :param ws_id: The workspace ID of the Project
    :param parent_id: The project ID
    :param service_id: the Service ID
    :return:
    """
    session = db_session()
    service = session.query(Service).filter_by(id=service_id).first()
    session.commit()
    if service:
        return service.as_dict()
    else:
        raise NotFound("No Service matching id {}".format(parent_id))


def validate_service_descriptor(workspace_path: str, descriptor: dict) -> None:
    """
    Validates the given descriptor with the schema loaded from SchemaValidator
    :param workspace_path: the path of the workspace
    :param descriptor: the service descriptor
    :raises: InvalidArgument: if the validation fails
    """
    schema = get_schema(workspace_path, SchemaValidator.SCHEMA_SERVICE_DESCRIPTOR)
    try:
        jsonschema.validate(descriptor, schema)
    except ValidationError as ve:
        raise InvalidArgument(ve.message)
