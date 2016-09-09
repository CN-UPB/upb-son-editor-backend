import shlex

from flask import request

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound, NameConflict
from son_editor.app.util import get_json
from son_editor.models.workspace import Workspace
from son_editor.models.repository import Catalogue


def get_catalogue(catalogue_id):
    session = db_session()
    catalogue = session.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    session.commit()
    if catalogue is None:
        raise NotFound("catalogue with id {} could not be found".format(catalogue_id))
    return catalogue.as_dict()


def get_catalogues(workspace_id):
    session = db_session()
    catalogues = session.query(Catalogue).filter(Catalogue.workspace_id == workspace_id).all()
    session.commit()
    return list(map(lambda x: x.as_dict(), catalogues))


def create_catalogue(workspace_id):
    catalogue_data = get_json(request)
    catalogue_name = shlex.quote(catalogue_data['name'])
    catalogue_url = shlex.quote(catalogue_data['url'])
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace is None:
        raise NotFound("workspace with id {} could not be found".format(workspace_id))

    existing_catalogues = session.query(Catalogue). \
        filter(Catalogue.workspace == workspace). \
        filter(Catalogue.name == catalogue_data['name']). \
        all()

    if len(existing_catalogues) > 0:
        raise NameConflict("catalogue with name {} already exists".format(catalogue_data['name']))
    catalogue = Catalogue(catalogue_name, catalogue_url, workspace)
    session.add(catalogue)
    session.commit()
    return catalogue.as_dict()


def update_catalogue(workspace_id, catalogue_id):
    catalogue_data = get_json(request)
    catalogue_name = shlex.quote(catalogue_data['name'])
    catalogue_url = shlex.quote(catalogue_data['url'])
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace is None:
        raise NotFound("workspace with id {} could not be found".format(workspace_id))

    catalogue = session.query(Catalogue). \
        filter(Catalogue.workspace == workspace). \
        filter(Catalogue.id == catalogue_id). \
        first()
    if catalogue is None:
        raise NotFound("catalogue with id {} could not be found".format(catalogue_id))

    if catalogue_name != catalogue.name:
        existing_catalogues = session.query(catalogue). \
            filter(catalogue.workspace == workspace). \
            filter(catalogue.name == catalogue_data['name']). \
            all()
        if len(existing_catalogues) > 0:
            raise NameConflict("catalogue with name {} already exists".format(catalogue_data['name']))

    catalogue.name = catalogue_name
    catalogue.url = catalogue_url
    session.commit()
    return catalogue.as_dict()


def delete(workspace_id, catalogue_id):
    session = db_session()
    workspace = session.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace is None:
        raise NotFound("workspace with id {} could not be found".format(workspace_id))

    catalogue = session.query(Catalogue). \
        filter(Catalogue.workspace == workspace). \
        filter(Catalogue.id == catalogue_id). \
        first()
    if catalogue is None:
        raise NotFound("catalogue with id {} could not be found".format(catalogue_id))

    session.delete(catalogue)
    session.commit()
    return catalogue.as_dict()
