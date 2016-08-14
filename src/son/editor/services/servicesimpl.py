import json
import shlex
from flask import Response
from flask.globals import request
from son.editor.models.project import Project
from son.editor.models.service import Service, ServiceEncoder
from son.editor.app.database import db_session
from son.editor.app.util import getJSON

session = db_session()


def get_services(wsID, parentID):
    project = Project.query.filter_by(id=parentID).first()
    if project is None:
        return "No project matching ID %i" % parentID
    else:
        response = Response(json.dumps(project.services))
        return response


def create_service(wsID, parentID):
    serviceData = getJSON(request)
    # Retrieve post parameters
    servicename = shlex.quote(serviceData["name"])
    vendorname = shlex.quote(serviceData["vendor"])
    version = shlex.quote(serviceData["version"])

    # Create db object
    service = Service(name=servicename, vendor = vendorname, version = version)
    session.add(service)

    session.commit()
    response = Response(mimetype='application/json',response=ServiceEncoder().encode(service), status=201)
    return response


def update_service(wsID, parentID, serviceID, serviceData):
    service = Service.query.filter.filter_by(id=serviceID).first()
    if service:
        # Parse parameters and update record
        serviceName = shlex.quote(serviceData["name"])
        if serviceName:
            service.name = serviceName
    else:
        return "Could not update service %i, because no record was found" % serviceID

    return "update service in project with id " + parentID


def delete_service(wsID, parentID, serviceID):
    return "deleted service from project with id " + parentID
