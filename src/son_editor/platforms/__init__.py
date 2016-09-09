from . import platformsapi


def init(api):
    api.add_namespace(platformsapi.namespace)
