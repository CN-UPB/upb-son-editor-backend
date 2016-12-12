import logging

from son_editor.app.database import db_session
from son_editor.app.exceptions import InvalidArgument
from son_editor.models.descriptor import Service
from son_editor.models.project import Project
from son_editor.models.repository import Platform
from son_editor.models.workspace import Workspace
from son_editor.util.publishutil import pack_project, push_to_platform, deploy_on_platform

logger = logging.getLogger(__name__)


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
            first()
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
        message = deploy_on_platform(service_uuid, platform)
        return {'message': 'Deployed successfully: {}'.format(message)}
    finally:
        session.commit()
