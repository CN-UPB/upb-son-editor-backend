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
    if project is None:
        raise NotFound("No project matching id {}".format(parentID))
    else:
        return list(map(lambda x: x.as_dict(), project.services))


def create_service(wsID, parentID):
    session = db_session()
    serviceData = getJSON(request)
    project = session.query(Project).filter_by(id=parentID).first()

    # Retrieve post parameters
    servicename = shlex.quote(serviceData["name"])
    vendorname = shlex.quote(serviceData["vendor"])
    version = shlex.quote(serviceData["version"])

    # Create db object
    service = Service(name=servicename, vendor=vendorname, version=version)

    session.add(service)
    project.services.append(service)
    session.commit()
    return service.as_dict()


def update_service(wsID, parentID, serviceID):
    session = db_session()
    serviceData = getJSON(request)
    service = session.query(Service).filter_by(id=serviceID).first()
    if service:
        # Parse parameters and update record
        servicename = shlex.quote(serviceData["name"])
        vendorname = shlex.quote(serviceData["vendor"])
        version = shlex.quote(serviceData["version"])
        if servicename:
            service.name = servicename
        if vendorname:
            service.vendor = vendorname
        if version:
            service.version = version
        session.commit()
        return service.as_dict()
    else:
        raise NotFound("Could not update service '{}', because no record was found".format(serviceID))


def delete_service(serviceID):
    session = db_session()
    service = session.query(Service).filter(Service.id == serviceID).first()
    if service:
        session.delete(service)
        session.commit()
    else:
        raise NotFound("Delete service did not work, {} not found".format(serviceID))
