from . import cataloguesapi


def init(api):
    api.add_namespace(cataloguesapi.namespace)
