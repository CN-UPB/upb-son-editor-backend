from . import projectsapi


def init(api):
    api.add_namespace(projectsapi.namespace)