import json
import logging
import os
from subprocess import Popen, PIPE

from son_editor.app.exceptions import PackException, ExtNotReachable, NameConflict
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace

logger = logging.getLogger(__name__)


def pack_project(project: Project) -> str:
    """
    Calls the son-package cli tool to pack the project and prepare it for deployment
    :param project: The project to pack
    :return:
    """
    ws_path = project.workspace.path
    pj_path = os.path.join(ws_path, 'projects', project.rel_path)
    proc = Popen(['son-package', '--workspace', ws_path, '--project', pj_path], stdout=PIPE, stderr=PIPE)

    out, err = proc.communicate()
    out = out.decode()
    err = err.decode()

    exitcode = proc.returncode
    if exitcode == 0:
        for line in err.splitlines():
            if line.find("File") >= 0:
                file_name = line[line.lower().find("file"):].split(" ", 1)[1]
                return file_name
    else:
        for line in err.splitlines():
            if line.find("ERROR") >= 0:
                error_message = line[line.find("ERROR"):]
                raise PackException(error_message)
    raise PackException(err)


def push_to_platform(package_path: str, ws: Workspace) -> str:
    """
    Pushes the package located at the package_path to the specified Platform
    :param package_path: the location of package to be pushed on disk
    :param platform: The platform to upload to
    :return:
    """
    proc = Popen(['son-access', "push", "--workspace", ws.path, '--upload', package_path], stdout=PIPE, stderr=PIPE)

    out, err = proc.communicate()
    out = out.decode()
    err = err.decode()

    logger.info("Out:" + out)
    logger.info("Error:" + err)

    exitcode = proc.returncode  # as of now exitcode is 0 even if there is an error
    if "ConnectionError" in out or "ConnectionError" in err:
        raise ExtNotReachable("Could not connect to platform.")
    elif "error" in out.lower() or "error" in err.lower():
        raise NameConflict("Out: " + out + "Error: " + err)
    elif "201" in out:
        start_index = out.index('{"service_uuid')
        end_index = out.index('}', start_index)
        out = out[start_index:end_index + 1]
        uuid = json.loads(out)
        return uuid
    else:
        return out

# Not Supported for now
# def deploy_on_platform(service_uuid: dict, platform: Platform) -> str:
#     """
#     Pushes the package located at the package_path to the specified Platform
#     :param service_uuid: a dictionary with the service uuid on the platform
#     :param platform: The platform to upload to
#     :return:
#     """
#     proc = Popen(['son-push', platform.url, '-D', str(service_uuid['service_uuid'])], stdout=PIPE, stderr=PIPE)
#
#     out, err = proc.communicate()
#     out = out.decode()
#     err = err.decode()
#
#     logger.info("Out:" + out)
#     logger.info("Error:" + err)
#
#     exitcode = proc.returncode  # as of now exitcode is 0 even if there is an error
#     if "ConnectionError" in out or err:
#         raise ExtNotReachable("Could not connect to platform.")
#     elif "error" in out.lower() or err.lower():
#         raise NameConflict("Out: " + out + "Error: " + err)
#     else:
#         return out
