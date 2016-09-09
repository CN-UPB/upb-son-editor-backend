from . import workspacesapi


def init(api):
    api.add_namespace(workspacesapi.namespace)
