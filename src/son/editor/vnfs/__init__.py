from . import functionsapi


def init(api):
    api.add_namespace(functionsapi.proj_namespace)
    api.add_namespace(functionsapi.cata_namespace)
    api.add_namespace(functionsapi.plat_namespace)