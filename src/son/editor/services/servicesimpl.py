import shlex
from flask.globals import request
from son.editor.models.project import Project
from son.editor.models.service import Service
from son.editor.app.database import db_session
from son.editor.app.util import getJSON


def get_services(wsID, parentID):
    project = Project.query.filter_by(id=parentID).first()
    if project is None:
        return "No project matching ID %i" % parentID
    else:
        return list(map(lambda x: x.as_dict(), project.services))


def create_service(wsID, parentID):
    session = db_session()
    serviceData = getJSON(request)
    # Retrieve post parameters
    servicename = shlex.quote(serviceData["name"])
    vendorname = shlex.quote(serviceData["vendor"])
    version = shlex.quote(serviceData["version"])

    # Create db object
    service = Service(name=servicename, vendor = vendorname, version = version)
    session.add(service)
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
        return "Could not update service '%i', because no record was found" % serviceID


def delete_service(serviceID):
    session = db_session()
    service = session.query(Service).filter_by(id=serviceID).first()
    if service:
        session.delete(service)
        session.commit()
    else:
        raise Exception("Delete service did not work, %s not found" % serviceID)
