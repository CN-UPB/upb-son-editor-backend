import logging

from son_editor.app.database import db_session
from son_editor.app.exceptions import InvalidArgument
from son_editor.impl.private_catalogue_impl import publish_private_nsfs, query_private_nsfs
from son_editor.models.descriptor import Service, Function
from son_editor.models.project import Project
from son_editor.models.repository import Platform
from son_editor.models.workspace import Workspace
from son_editor.util.publishutil import pack_project, push_to_platform

logger = logging.getLogger(__name__)


def publish_referenced_functions(ws_id, proj_id, descriptor):
    vnfs = descriptor["network_functions"]
    session = db_session()
    for vnf in vnfs:
        function = session.query(Function).join(Project). \
            filter(Project.id == proj_id). \
            filter(Function.name == vnf['vnf_name']). \
            filter(Function.vendor == vnf["vnf_vendor"]). \
            filter(Function.version == vnf["vnf_version"]).first()
        publish_private_nsfs(ws_id, function.as_dict()["descriptor"], True)


def create_service_on_platform(ws_id, platform_id, service_data):
    """
    Deploys the service on the referenced Platform

    :param ws_id:
    :param platform_id:
    :param service_data:
    :return: A  message if the function was deployed successfully
    """
    service_id = int(service_data['id'])
    session = db_session()
    try:
        workspace = session.query(Workspace).filter(Workspace.id == ws_id).first()
        project = session.query(Project). \
            join(Service). \
            filter(Project.services.any(Service.id == service_id)). \
            filter(Project.workspace == workspace). \
            first()  # type: Project
        if not len(project.services) == 1:
            raise InvalidArgument(
                "Project must have exactly one service "
                "to push to platform. Number of services: {}".format(
                    len(project.services)))

        platform = session.query(Platform).filter(Platform.id == platform_id). \
            filter(Platform.workspace == workspace).first()
        package_path = pack_project(project)
        service_uuid = push_to_platform(package_path, platform)
        logger.info("Pushed to platform: " + str(service_uuid))
        # deploy to private catalogue
        service = project.services[0].as_dict()
        publish_private_nsfs(ws_id, service["descriptor"], is_vnf=False)
        publish_referenced_functions(ws_id, project.id, service["descriptor"])
        return {'message': 'Deployed successfully: {}'.format(str(service_uuid))}
    finally:
        session.commit()
