import json

import yaml


def load_from_disk(file, descriptor_model):
    with open(file, 'r') as stream:
        descriptor = yaml.safe_load(stream)
        descriptor_model.__init__(descriptor=json.dumps(descriptor),
                                  name=descriptor['name'],
                                  vendor=descriptor['vendor'],
                                  version=descriptor['version'])


def write_to_disk(folder, descriptor_model):
    with open(get_file_name(folder, descriptor_model), 'w') as stream:
        data = json.loads(descriptor_model.descriptor)
        yaml.safe_dump(data, stream, default_flow_style=False)


def get_file_name(folder, model):
    project = model.project
    workspace = project.workspace
    return workspace.path + "/projects/" \
           + project.rel_path + "/sources/" \
           + folder + "/" \
           + model.vendor + "-" \
           + model.name + "-" \
           + model.version + ".yml"
