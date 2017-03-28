import shlex

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound, NameConflict
from son_editor.models.repository import Catalogue
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import update_workspace_descriptor


def get_catalogue(catalogue_id):
    """
    Retrieves a catalogue by its id

    :param catalogue_id: The catalogues ID
    :return:
    """
    session = db_session()
    catalogue = session.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    session.commit()
    if catalogue is None:
        raise NotFound("catalogue with id {} could not be found".format(catalogue_id))
    return catalogue.as_dict()


def get_catalogues(workspace_id):
    """
    Retrieves all catalogues of a specific workspace

    :param workspace_id: the workspace id
    :return: list of catalogue descriptors of this workspace
    """
    session = db_session()
    catalogues = session.query(Catalogue).filter(Catalogue.workspace_id == workspace_id).all()
    session.commit()
    return list(map(lambda x: x.as_dict(), catalogues))


def create_catalogue(workspace_id: int, catalogue_data):
    """
    Creates a catalgoue in the given workspace. A catalogue is defined by its name and url. These are given as
    json data

    :param workspace_id: Workspace ID of the target workspace, where the catalogue should get created.
    :return: Catalogue descriptor
    """
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
    catalogue = Catalogue(name=catalogue_name, url=catalogue_url, workspace=workspace)
    session.add(catalogue)
    session.commit()
    update_workspace_descriptor(catalogue.workspace)
    return catalogue.as_dict()


def update_catalogue(workspace_id, catalogue_id, catalogue_data):
    """
    Updates a specific catalogue by its id. The catalogue
    applies the given name and url, that are in the json parameter.
    :param workspace_id: The Workspace ID
    :param catalogue_id: The Catalogue ID
    :return: The updated Catalogue descriptor
    """
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
    update_workspace_descriptor(catalogue.workspace)
    return catalogue.as_dict()


def delete(workspace_id, catalogue_id):
    """
    Deletes a catalogue by its id

    :param workspace_id: The workspace ID
    :param catalogue_id: The Catalogue ID
    :return: The deleted catalogue descriptor
    """
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
    update_workspace_descriptor(catalogue.workspace)
    return catalogue.as_dict()
