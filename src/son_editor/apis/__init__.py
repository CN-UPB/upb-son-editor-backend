from son_editor.apis import misc
from son_editor.apis import cataloguesapi
from son_editor.apis import platformsapi
from son_editor.apis import projectsapi
from son_editor.apis import servicesapi
from son_editor.apis import functionsapi
from son_editor.apis import workspacesapi
from son_editor.apis import nsfslookup
from son_editor.apis import userserviceapi
from son_editor.apis import gitapi


def init(api):
    api.add_namespace(workspacesapi.namespace)
    api.add_namespace(functionsapi.proj_namespace)
    api.add_namespace(functionsapi.cata_namespace)
    api.add_namespace(functionsapi.plat_namespace)
    api.add_namespace(servicesapi.proj_namespace)
    api.add_namespace(servicesapi.cata_namespace)
    api.add_namespace(servicesapi.plat_namespace)
    api.add_namespace(projectsapi.namespace)
    api.add_namespace(platformsapi.namespace)
    api.add_namespace(cataloguesapi.namespace)
    api.add_namespace(misc.namespace)
    api.add_namespace(nsfslookup.namespace)
    api.add_namespace(userserviceapi.namespace)
    api.add_namespace(gitapi.namespace)
