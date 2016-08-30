from . import servicesapi


def init(api):
    api.add_namespace(servicesapi.proj_namespace)
    api.add_namespace(servicesapi.cata_namespace)
    api.add_namespace(servicesapi.plat_namespace)
