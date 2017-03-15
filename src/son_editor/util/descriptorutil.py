import json
import os

import yaml
from urllib import request

from son_editor.util.requestutil import get_config

SCHEMA_ID_VNF = "vnf"
SCHEMA_ID_NS = "ns"

schemas = {}


def load_ns_vnf_from_disk(file: str, model):
    """
    Loads a vnf or network service descriptor from disk and initializes the given model

    :param file: the file path of the descriptor
    :param model: The database  model of the descriptor
    :return: the given updated model
    """
    with open(file, 'r') as stream:
        descriptor = yaml.safe_load(stream)
        model.__init__(descriptor=json.dumps(descriptor),
                       name=descriptor['name'],
                       vendor=descriptor['vendor'],
                       version=descriptor['version'])
        return model


def write_ns_vnf_to_disk(folder: str, model) -> None:
    """
    Saves the given model to disk as a yml file

    :param folder: the folder to write to, either "vnf" or "nsd"
    to specify if a vnf or network service needs to be saved
    :param model: The database  model of the descriptor
    :return:
    """
    target_dir = os.path.dirname(get_file_path(folder, model))
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    with open(get_file_path(folder, model), 'w') as stream:
        data = json.loads(model.descriptor)
        yaml.safe_dump(data, stream, default_flow_style=False)


def get_file_path(folder: str, model) -> str:
    """
    Returns the filepath to the descriptor computed
    from the models vendor name and version

    :param folder: the folder to write to, either "vnf" or "nsd"
    to specify if a vnf or network service needs to be saved
    :param model: The database  model of the descriptor
    :return:
    """
    project = model.project
    workspace = project.workspace
    return os.path.join(workspace.path,
                        "projects",
                        project.rel_path,
                        "sources",
                        folder,
                        (model.name + os.path.sep if folder == "vnf" else ""),
                        get_file_name(model))


def get_file_name(model) -> str:
    """
    Get the standard file name for a descriptor

    :param model: The database  model of the descriptor
    :return: The standard descriptor file name, computed from the models vendor name and version
    """
    return "{}-{}-{}.yml".format(model.vendor,
                                 model.name,
                                 model.version)


def update_workspace_descriptor(workspace) -> None:
    """
    Updates the workspace descriptor with data from the workspace model

    :param workspace: The workspace model
    :return:
    """
    with open(os.path.join(workspace.path, "workspace.yml"), "r") as stream:
        ws_descriptor = yaml.safe_load(stream)

    ws_descriptor['catalogue_servers'] = []
    for cat in workspace.catalogues:
        catalogue_server = {'id': cat.name, 'url': cat.url, 'publish': cat.publish}
        ws_descriptor['catalogue_servers'].append(catalogue_server)
    ws_descriptor['service_platforms'] = {}
    ws_descriptor['default_service_platform'] = ''
    for plat in workspace.platforms:
        platform_server = {'url': plat.url, "credentials": {"token_file": plat.token_path}}
        ws_descriptor['service_platforms'][plat.name] = platform_server
        if plat.publish:
            ws_descriptor['default_service_platform'] = plat.name
    if not ws_descriptor['default_service_platform'] and ws_descriptor['service_platforms']:
        # if no default set, select "first" platform
        ws_descriptor['default_service_platform'] = \
            ws_descriptor['service_platforms'][ws_descriptor['service_platforms'].keys()[0]]['id']
    ws_descriptor['name'] = workspace.name
    ws_descriptor['ns_schema_index'] = workspace.ns_schema_index
    ws_descriptor['vnf_schema_index'] = workspace.vnf_schema_index

    with open(os.path.join(workspace.path, "workspace.yml"), "w") as stream:
        yaml.safe_dump(ws_descriptor, stream)


def load_workspace_descriptor(workspace) -> None:
    """
    Loads the workspace descriptor from disk and updates the database model

    :param workspace: The workspace database model
    :return:
    """
    from son_editor.models.repository import Catalogue
    from son_editor.models.repository import Platform

    with open(os.path.join(workspace.path, "workspace.yml"), "r") as stream:
        ws_descriptor = yaml.safe_load(stream)
        if 'catalogue_servers' in ws_descriptor:
            catalogues = ws_descriptor['catalogue_servers']
            for catalogue_server in catalogues:
                workspace.catalogues.append(Catalogue(name=catalogue_server['id'],
                                                      url=catalogue_server['url'],
                                                      publish=catalogue_server['publish'] == 'yes'))
        if 'service_platforms' in ws_descriptor:
            platforms = ws_descriptor['service_platforms']
            for platform_id, platform in platforms.items():
                workspace.platforms.append(Platform(name=platform_id,
                                                    url=platform['url'],
                                                    publish=ws_descriptor['default_service_platform'] == platform_id))
        if 'ns_schema_index' in ws_descriptor:
            workspace.ns_schema_index = ws_descriptor['ns_schema_index']
        if 'vnf_schema_index' in ws_descriptor:
            workspace.vnf_schema_index = ws_descriptor['vnf_schema_index']


def load_project_descriptor(project) -> dict:
    """Loads the project descriptor from disk"""
    with open(os.path.join(project.workspace.path, "projects", project.rel_path, "project.yml"), "r") as stream:
        return yaml.safe_load(stream)


def write_project_descriptor(project, project_descriptor):
    """Writes the project database model to disk"""
    with open(os.path.join(project.workspace.path, "projects", project.rel_path, "project.yml"), "w") as stream:
        return yaml.safe_dump(project_descriptor, stream)


def sync_project_descriptor(project) -> None:
    """
    Updates the project model with data from the project descriptor and vice versa

    :param project: The projects database model
    :return:
    """
    project_descriptor = load_project_descriptor(project)
    project_descriptor['name'] = project.name
    if project.description is not None:
        project_descriptor['description'] = project.description
    elif 'description' in project_descriptor:
        project.description = project_descriptor['description']

    if project.maintainer is not None:
        project_descriptor['maintainer'] = project.maintainer
    elif 'maintainer' in project_descriptor:
        project.maintainer = project_descriptor['maintainer']

    if project.vendor is not None:
        project_descriptor['vendor'] = project.vendor
    elif 'vendor' in project_descriptor:
        project.vendor = project_descriptor['vendor']

    if project.version is not None:
        project_descriptor['version'] = project.version
    elif 'version' in project_descriptor:
        project.version = project_descriptor['version']

    if project.publish_to is not None:
        project_descriptor['publish_to'] = project.publish_to.split(',')
    elif 'publish_to' in project_descriptor:
        project.publish_to = ','.join(project_descriptor['publish_to'])

    if project.repo_url is not None:
        project_descriptor['repo_url'] = project.repo_url
    elif 'repo_url' in project_descriptor:
        project.repo_url = project_descriptor['repo_url']

    write_project_descriptor(project, project_descriptor)


def load_schemas():
    schemas[SCHEMA_ID_VNF] = []
    for vnf_schema in get_config()["schemas"][SCHEMA_ID_VNF]:
        response = request.urlopen(vnf_schema['url'])
        data = response.read()
        vnf_schema['schema'] = yaml.safe_load(data.decode('utf-8'))
        schemas[SCHEMA_ID_VNF].append(vnf_schema)
    schemas[SCHEMA_ID_NS] = []
    for ns_schema in get_config()["schemas"][SCHEMA_ID_NS]:
        response = request.urlopen(ns_schema['url'])
        data = response.read()
        ns_schema['schema'] = yaml.safe_load(data.decode('utf-8'))
        schemas[SCHEMA_ID_NS].append(ns_schema)


def get_schemas():
    if not schemas:
        load_schemas()
    return schemas


def get_schema(schema_index, schema_id: str) -> dict:
    if schema_id not in schemas:
        load_schemas()

    return schemas[schema_id][schema_index]["schema"]


def write_private_descriptor(workspace_path: str, is_vnf: bool, descriptor: dict):
    type_folder = "ns"
    if is_vnf:
        type_folder = "vnf"
    dirs = os.path.join(workspace_path,
                        type_folder,
                        descriptor['vendor'],
                        descriptor['name'],
                        descriptor['version'])
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    file_path = os.path.join(dirs, "descriptor.yml")
    with open(file_path, "w") as stream:
        return yaml.safe_dump(descriptor, stream)
