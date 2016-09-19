import os
from subprocess import Popen, PIPE

from son_editor.app.exceptions import PackException
from son_editor.models.project import Project
from son_editor.models.repository import Platform


def pack_project(project: Project) -> str:
    ws_path = project.workspace.path
    pj_path = os.path.join(ws_path, 'projects', project.rel_path)
    proc = Popen(['son-package','--workspace', ws_path, '--project', pj_path], stdout=PIPE, stderr=PIPE)

    out, err = proc.communicate()
    out= out.decode()
    err = err.decode()

    exitcode = proc.returncode
    if exitcode == 0:
        for line in err.splitlines():
            if line.find("File") >=0:
                file_name = line[line.lower().find("file"):].split(" ",1)[1]
                return file_name
    else:
        for line in err.splitlines():
            if line.find("ERROR") >=0:
                error_message = line[line.find("ERROR"):]
                raise PackException(error_message)
    raise PackException(err)

def push_to_platform(package_path: str, platform: Platform) -> bool:
    proc = Popen(['son-push', platform.url, '-U', package_path], stdout=PIPE, stderr=PIPE)

    print(proc.communicate())

    exitcode = proc.returncode
    return exitcode == 0
