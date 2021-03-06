from son_editor.apis import configapi
from son_editor.apis import misc
from son_editor.apis import cataloguesapi
from son_editor.apis import catalogue_functionsapi
from son_editor.apis import catalogue_servicesapi
from son_editor.apis import platformsapi
from son_editor.apis import projectsapi
from son_editor.apis import project_servicesapi
from son_editor.apis import project_functionsapi
from son_editor.apis import workspacesapi
from son_editor.apis import nsfslookup
from son_editor.apis import userserviceapi
from son_editor.apis import gitapi
from son_editor.apis import schemaapi


def init(api):
    api.add_namespace(workspacesapi.namespace)
    api.add_namespace(project_functionsapi.namespace)
    api.add_namespace(catalogue_functionsapi.namespace)
    api.add_namespace(project_servicesapi.namespace)
    api.add_namespace(catalogue_servicesapi.namespace)
    api.add_namespace(projectsapi.namespace)
    api.add_namespace(platformsapi.namespace)
    api.add_namespace(cataloguesapi.namespace)
    api.add_namespace(misc.namespace)
    api.add_namespace(nsfslookup.namespace)
    api.add_namespace(userserviceapi.namespace)
    api.add_namespace(gitapi.namespace)
    api.add_namespace(schemaapi.namespace)
    api.add_namespace(configapi.namespace)
