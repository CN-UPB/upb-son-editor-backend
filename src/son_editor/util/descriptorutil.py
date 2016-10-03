import json
import os

import yaml

def load_from_disk(file, model):
    with open(file, 'r') as stream:
        descriptor = yaml.safe_load(stream)
        model.__init__(descriptor=json.dumps(descriptor),
                       name=descriptor['name'],
                       vendor=descriptor['vendor'],
                       version=descriptor['version'])
        return model


def write_to_disk(folder: str, model):
    target_dir = os.path.dirname(get_file_path(folder, model))
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    with open(get_file_path(folder, model), 'w') as stream:
        data = json.loads(model.descriptor)
        yaml.safe_dump(data, stream, default_flow_style=False)


def get_file_path(folder: str, model) -> str:
    project = model.project
    workspace = project.workspace
    return workspace.path + "/projects/" \
           + project.rel_path + "/sources/" \
           + folder + "/" \
           + (model.name + "/" if folder == "vnf" else "") \
           + get_file_name(model)


def get_file_name(model) -> str:
    return model.vendor + "-" \
           + model.name + "-" \
           + model.version + ".yml"


def synchronize_workspace_descriptor(workspace, session):
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


def update_workspace_descriptor(workspace):
    with open(os.path.join(workspace.path, "workspace.yml"), "r+") as stream:
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
        yaml.safe_dump(ws_descriptor, stream)


def load_workspace_descriptor(workspace):
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
