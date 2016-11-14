import logging
import os
from subprocess import Popen, PIPE

from son_editor.app.exceptions import PackException, ExtNotReachable, NameConflict
from son_editor.models.project import Project
from son_editor.models.repository import Platform

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


def push_to_platform(package_path: str, platform: Platform) -> str:
    """
    Pushes the package located at the package_path to the specified Platform
    :param package_path: the location of package to be pushed on disk
    :param platform: The platform to upload to
    :return:
    """
    logger.warn(package_path)
    proc = Popen(['son-push', platform.url, '-U', package_path], stdout=PIPE, stderr=PIPE)

    out, err = proc.communicate()
    out = out.decode()
    err = err.decode()

    logger.info("Out:" + out)
    logger.info("Error:" + err)

    exitcode = proc.returncode  # as of now exitcode is 0 even if there is an error
    if "ConnectionError" in out or err:
        raise ExtNotReachable("Could not connect to platform.")
    elif "error" in out.lower() or err.lower():
        raise NameConflict("Out: " + out + "Error: " + err)
    elif "201" or "200" in out:
        logger.warn(out)
        message = out.split(":", 1)[1]
        return message
    else:
        return out
