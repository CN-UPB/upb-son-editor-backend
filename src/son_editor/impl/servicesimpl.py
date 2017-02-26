import json
import logging
import os
import shlex
import shutil

import jsonschema
from jsonschema import ValidationError

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound, NameConflict, InvalidArgument, StillReferenced
from son_editor.models.descriptor import Service
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import write_ns_vnf_to_disk, get_file_path, get_schema, SCHEMA_ID_NS

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
        validate_service_descriptor(workspace.ns_schema_index, service_data["descriptor"])

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
    project = session.query(Project). \
        filter(Project.id == project_id).first()
    service = session.query(Service). \
        join(Project). \
        join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Service.project == project). \
        filter(Service.id == service_id).first()
    if service:
        refs = get_references(service, session)
        old_file_name = get_file_path("nsd", service)
        old_uid = get_uid(service.vendor, service.name, service.version)
        # Parse parameters and update record
        if 'descriptor' in service_data:
            # validate service descriptor
            workspace = session.query(Workspace).filter(Workspace.id == ws_id).first()
            validate_service_descriptor(workspace.ns_schema_index, service_data["descriptor"])
            try:
                newName = shlex.quote(service_data["descriptor"]["name"])
                newVendor = shlex.quote(service_data["descriptor"]["vendor"])
                newVersion = shlex.quote(service_data["descriptor"]["version"])
            except KeyError as ke:
                raise InvalidArgument("Missing key {} in function data".format(str(ke)))
            new_uid = get_uid(newVendor, newName, newVersion)
            if old_uid != new_uid:
                if refs:
                    # keep old version and create new version in db
                    service = Service(newName, newVersion, newVendor, project=project)
                    session.add(service)
                else:
                    service.name = newName
                    service.vendor = newVendor
                    service.version = newVersion
            service.descriptor = json.dumps(service_data["descriptor"])

        if 'meta' in service_data:
            service.meta = json.dumps(service_data["meta"])

        if old_uid != new_uid:
            new_file_name = get_file_path("nsd", service)
            try:
                if not old_file_name == new_file_name:
                    if refs:
                        shutil.copy(old_file_name, new_file_name)
                    else:
                        shutil.move(old_file_name, new_file_name)
                write_ns_vnf_to_disk("nsd", service)
            except:
                logger.exception("Could not update descriptor file:")
                raise
        session.commit()
        return service.as_dict()
    else:
        raise NotFound("Could not update service '{}', because no record was found".format(service_id))


def replace_service_refs(refs, vendor, name, version, new_vendor, new_name, new_version):
    for service in refs:
        service_desc = json.loads(service.descriptor)
        for ref in service_desc['network_services']:
            if ref['vnf_vendor'] == vendor \
                    and ref['vnf_name'] == name \
                    and ref['vnf_version'] == version:
                ref['vnf_vendor'] = new_vendor
                ref['vnf_name'] = new_name
                ref['vnf_version'] = new_version
        if 'services_dependencies' in service_desc:
            for ref in service_desc['services_dependencies']:
                if ref['vendor'] == vendor \
                        and ref['name'] == name \
                        and ref['version'] == version:
                    ref['vendor'] = new_vendor
                    ref['name'] = new_name
                    ref['version'] = new_version
        service.descriptor = json.dumps(service_desc)


def get_uid(vendor, name, version):
    return "{}:{}:{}".format(vendor, name, version)


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

    refs = get_references(service, session)
    if refs:
        session.rollback()
        ref_str = ",\n".join(ref.uid for ref in refs)
        raise StillReferenced("Could not delete service because it is still referenced by \n" + ref_str)
    session.delete(service)
    try:
        os.remove(get_file_path("nsd", service))
    except:
        session.rollback()
        logger.exception("Could not delete service:")
        raise
    session.commit()
    return service.as_dict()


def get_references(service, session):
    references = []
    # fuzzy search to get all services that have all strings
    maybe_references = session.query(Service). \
        filter(Service.project == service.project). \
        filter(Service.id != service.id). \
        filter(Service.descriptor.like("%" + service.name + "%")). \
        filter(Service.descriptor.like("%" + service.vendor + "%")). \
        filter(Service.descriptor.like("%" + service.version + "%")).all()
    # check that strings are really a reference to this function
    for ref_service in maybe_references:
        descriptor = json.loads(ref_service.descriptor)
        if "network_services" in descriptor:
            for ref in descriptor["network_services"]:
                if ref['ns_name'] == service.name \
                        and ref['ns_vendor'] == service.vendor \
                        and ref['ns_version'] == service.version:
                    references.append(service)
    return references


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


def validate_service_descriptor(schema_index: int, descriptor: dict) -> None:
    """
    Validates the given descriptor with the schema loaded from the configuration

    :param schema_index: the workspace
    :param descriptor: the service descriptor
    :raises: InvalidArgument: if the validation fails
    """
    schema = get_schema(schema_index, SCHEMA_ID_NS)
    try:
        jsonschema.validate(descriptor, schema)
    except ValidationError as ve:
        raise InvalidArgument("Validation failed: <br/> Path: {} <br/> Error: {}".format(list(ve.path), ve.message))
