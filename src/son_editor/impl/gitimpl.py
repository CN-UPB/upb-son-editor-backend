import logging
import os
from subprocess import Popen, PIPE
from urllib import parse

from flask import session

from son_editor.app.database import db_session
from son_editor.app.exceptions import NotFound, InvalidArgument
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace

# Github domains to check if github is used
GITHUB_DOMAINS = ['github.com', 'www.github.com']
PROJECT_REL_PATH = "/projects"

logger = logging.getLogger(__name__)


def is_github(netloc):
    """ Checks if the given url is on github """
    if netloc.lower() in GITHUB_DOMAINS:
        return True
    return False


def git_command(git_args: list, cwd: str = None):
    """
    Calls the git command with given args and returns out, err and exitcode
    :param git_args: Arguments for git
    :param cwd: Optional current working directory
    :return: out, error, exitcode
    """
    args = ['git'].join(git_args)
    git_process = Popen(args,
                        stdout=PIPE, stderr=PIPE, cwd=cwd)

    out, err = git_process.communicate()
    exitcode = git_process.returncode
    return out.decode(), err.decode(), exitcode


def create_info_dict(out: str = None, err: str = None, exitcode: int = 0) -> dict:
    """
    Creates a dict that holds process information
    :param out: Out bytes
    :param err: Err bytes
    :param exitcode: exitcode
    :return: Dict with packed information.
    """
    # Empty result_dict
    result_dict = {'success': exitcode is 0}

    if out:
        result_dict.update({'out': out})
    if err:
        result_dict.update({'err': err})
    if exitcode:
        result_dict.update({'exitcode': exitcode})
    return result_dict


def get_project(pj_id: int) -> Project:
    project = db_session().query(Project).filter(Project.id == pj_id).first()
    if not project:
        raise NotFound("Could not find project with id {}".format(pj_id))
    return project


def get_workspace(ws_id: int) -> Workspace:
    workspace = db_session().query(Workspace).filter(Workspace.id == ws_id).first()
    if not workspace:
        raise NotFound("Could not find workspace with id {}".format(ws_id))
    return workspace


def commit(project_id: int, commit_message: str):
    project = get_project(project_id)

    project_full_path = project.workspace.path + project.rel_path
    # Add all stuff and modified files
    out, err, exitcode = git_command(['add', '-A'], cwd=project_full_path)
    if exitcode is not 0:
        return create_info_dict(err, exitcode)

    # Commit with message
    out, err, exitcode = git_command(['commit', "-m '{}'".format(commit_message)], cwd=project_full_path)
    if exitcode is not 0:
        return create_info_dict(err, exitcode)

    # Success on commit
    return create_info_dict(out)


def pull(project_id: int):
    """
    Pulls data from the given project_id.
    :param user_data: Session data to get access token for GitHub
    :param ws_id:
    :param project_id:
    :return:
    """
    project = get_project(project_id)

    project_full_path = project.workspace.path + project.rel_path

    # Error handling
    if not os.path.isdir(project_full_path):
        raise Exception("Could not find project directory {}".format(project_full_path))

    if not project.repo_url:
        raise InvalidArgument("Project with id {} is missing the repo attribute".format(project_id))

    # Pull in project directory
    # If url in GitHub domain, access by token
    out, err, exitcode = git_command(['pull', project.repo_url], cwd=project_full_path)

    if exitcode is not 0:
        return create_info_dict(err=err, exitcode=exitcode)
    return create_info_dict(out=out, err=err, exitcode=exitcode)


def clone(user_data, ws_id: int, url: str):
    """
    Clones a repository by url into given workspace
    :param user_data: Session data to get access token for GitHub
    :param ws_id: Destination workspace to clone
    :param url: URL of the source repository
    :return: True if successful, otherwise NameConflict is thrown
    """
    workspace = get_workspace(ws_id)
    url_decode = parse.urlparse(url)

    if is_github(url_decode.netloc):
        # Take the suffix of url as first name candidate
        project_target_name = os.path.split(url_decode.path)[-1]
        project_target_path = workspace.path + "/" + PROJECT_REL_PATH + "/" + project_target_name

        # If url in GitHub domain, access by token
        logger.info('Cloning from github repo...')
        url_with_token = 'https://{}@github.com/{}'.format(session['access_token'], url_decode.path)
        out, err, exitcode = git_command(['clone', url_with_token, project_target_path])

        if exitcode is not 0:
            return create_info_dict(err=err, exitcode=exitcode)

    else:
        raise NotImplemented("Cloning from other is not implemented yet. Only github supported for now.")

    return create_info_dict(out=out)
