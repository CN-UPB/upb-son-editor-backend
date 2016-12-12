import json
import os

import yaml
from son.schema.validator import SchemaValidator


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


def synchronize_workspace_descriptor(workspace, session) -> None:
    """
    Updates both the workspace descriptor on disk and in
     the database to contain the same essential data
    :param workspace: the database workspace model
    :param session: the current database session
    :return:
    """
    from son_editor.models.repository import Catalogue
    with open(os.path.join(workspace.path, "workspace.yml"), "r+") as stream:
        ws_descriptor = yaml.safe_load(stream)
        if "catalogue_servers" not in ws_descriptor:
            ws_descriptor["catalogue_servers"] = []
        for catalogue_server in ws_descriptor["catalogue_servers"]:
            if len([x for x in workspace.catalogues if x.name == catalogue_server['id']]) == 0:
                session.add(Catalogue(name=catalogue_server['id'],
                                      url=catalogue_server['url'],
                                      publish=catalogue_server['publish'] == 'yes',
                                      workspace=workspace)
                            )
        for cat in workspace.catalogues:
            if len([x for x in ws_descriptor["catalogue_servers"] if x['id'] == cat.name]) == 0:
                catalogue_server = {'id': cat.name, 'url': cat.url, 'publish': cat.publish}
                ws_descriptor['catalogue_servers'].append(catalogue_server)
        ws_descriptor['name'] = workspace.name
        yaml.safe_dump(ws_descriptor, stream)


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
        ws_descriptor['platform_servers'] = []
        for plat in workspace.platforms:
            platform_server = {'id': plat.name, 'url': plat.url, 'publish': plat.publish}
            ws_descriptor['platform_servers'].append(platform_server)
        ws_descriptor['name'] = workspace.name
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
        if 'platform_servers' in ws_descriptor:
            platforms = ws_descriptor['platform_servers']
            for platform_server in platforms:
                workspace.platforms.append(Platform(name=platform_server['id'],
                                                    url=platform_server['url'],
                                                    publish=platform_server['publish'] == 'yes'))


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


def get_schema(ws_path: str, schema_id : str) -> dict:
    from son.workspace.workspace import Workspace

    workspace = Workspace(ws_path)
    return SchemaValidator(workspace).load_schema(schema_id)
