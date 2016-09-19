import shlex

from flask import request

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound, NameConflict
from son_editor.models.repository import Platform
from son_editor.models.workspace import Workspace
from son_editor.util.requestutil import get_json


def get_platform(platform_id):
    session = db_session()
    platform = session.query(Platform).filter(Platform.id == platform_id).first()
    session.commit()
    if platform is None:
        raise NotFound("Platform with id {} could not be found".format(platform_id))
    return platform.as_dict()


def get_platforms(workspace_id):
    session = db_session()
    platforms = session.query(Platform).filter(Platform.workspace_id == workspace_id).all()
    session.commit()
    return list(map(lambda x: x.as_dict(), platforms))


def create_platform(workspace_id):
    platform_data = get_json(request)
    platform_name = shlex.quote(platform_data['name'])
    platform_url = shlex.quote(platform_data['url'])
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace is None:
        raise NotFound("workspace with id {} could not be found".format(workspace_id))

    existing_platforms = session.query(Platform). \
        filter(Platform.workspace == workspace). \
        filter(Platform.name == platform_data['name']). \
        all()

    if len(existing_platforms) > 0:
        raise NameConflict("Platform with name {} already exists".format(platform_data['name']))
    platform = Platform(platform_name, platform_url, workspace)
    session.add(platform)
    session.commit()
    return platform.as_dict()


def update_platform(workspace_id, platform_id):
    platform_data = get_json(request)
    platform_name = shlex.quote(platform_data['name'])
    platform_url = shlex.quote(platform_data['url'])
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace is None:
        raise NotFound("workspace with id {} could not be found".format(workspace_id))

    platform = session.query(Platform). \
        filter(Platform.workspace == workspace). \
        filter(Platform.id == platform_id). \
        first()
    if platform is None:
        raise NotFound("Platform with id {} could not be found".format(platform_id))

    if platform_name != platform.name:
        existing_platforms = session.query(Platform). \
            filter(Platform.workspace == workspace). \
            filter(Platform.name == platform_data['name']). \
            all()
        if len(existing_platforms) > 0:
            raise NameConflict("Platform with name {} already exists".format(platform_data['name']))

    platform.name = platform_name
    platform.url = platform_url
    session.commit()
    return platform.as_dict()


def delete(workspace_id, platform_id):
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace is None:
        raise NotFound("workspace with id {} could not be found".format(workspace_id))

    platform = session.query(Platform). \
        filter(Platform.workspace == workspace). \
        filter(Platform.id == platform_id). \
        first()
    if platform is None:
        raise NotFound("Platform with id {} could not be found".format(platform_id))

    session.delete(platform)
    session.commit()
    return platform.as_dict()