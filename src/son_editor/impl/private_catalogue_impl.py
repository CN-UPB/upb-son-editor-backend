import json

from son_editor.app.database import db_session
from son_editor.app.exceptions import InvalidArgument
from son_editor.models.private_descriptor import PrivateDescriptor
from son_editor.models.private_descriptor import PrivateService, PrivateFunction
from son_editor.impl.usermanagement import get_user
from son_editor.models.workspace import Workspace
from son_editor.util.descriptorutil import write_private_descriptor


def publish_private_nsfs(ws_id: int, descriptor: dict, is_vnf: bool):
    """
    Publishes a function or service to the private catalogue repository

    :param ws_id:
    :param descriptor:
    :param is_vnf:
    :return:
    """
    try:
        name = descriptor['name']
        vendor = descriptor['vendor']
        version = descriptor['version']
    except KeyError as ke:
        raise InvalidArgument("Missing key {} in descriptor data".format(str(ke)))

    try:
        session = db_session
        # create or update descriptor in database
        model = query_private_nsfs(ws_id, vendor, name, version, is_vnf)  # type: PrivateDescriptor
        if model is None:
            if is_vnf:
                model = PrivateFunction()
            else:
                model = PrivateService()

            model.__init__(ws_id, vendor, name, version)
            session.add(model)
        model.descriptor = json.dumps(descriptor)
        workspace = session.query(Workspace).filter(Workspace.id == ws_id).first()
        if workspace is not None:
            write_private_descriptor(workspace.path, is_vnf, descriptor)
            session.commit()
            return
    except:
        session.rollback()
        raise


def query_private_nsfs(ws_id, vendor, name, version, is_vnf):
    """
    Finds a function in the private catalogue

    :param ws_id:
    :param is_vnf:
    :param vendor:
    :param name:
    :param version:
    :return:
    """
    session = db_session()
    if is_vnf:
        descriptor = session.query(PrivateFunction).filter(PrivateFunction.name == name and
                                                           PrivateFunction.vendor == vendor and
                                                           PrivateFunction.version == version and
                                                           PrivateFunction.workspace.id == ws_id and
                                                           PrivateFunction.workspace.owner == get_user(
                                                               session['user_data'])).first()
    else:
        descriptor = session.query(PrivateService).filter(
            PrivateService.name == name and
            PrivateService.vendor == vendor and
            PrivateService.version == version and
            PrivateFunction.workspace.id == ws_id and
            PrivateFunction.workspace.owner == get_user(session['user_data'])).first()
    return descriptor


def get_private_nsfs_list(ws_id, is_vnf):
    """
    Get a list of all private services or functions

    :param ws_id: the Workspace ID
    :param is_vnf: if vnf or services should be queried
    :return: List of all private services or functions
    """
    session = db_session()
    descriptors = None
    if is_vnf:
        descriptors = session.query(PrivateFunction).join(Workspace).filter(Workspace.id == ws_id).all()
    else:
        descriptors = session.query(PrivateService).join(Workspace).filter(Workspace.id == ws_id).all()
    return list(map(lambda x: x.as_dict(), descriptors))
