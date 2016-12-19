import logging
import os
from subprocess import Popen, PIPE
from urllib import parse

import shutil
from flask import session
from networkx.algorithms.bipartite.projection import project

from son_editor.util.constants import PROJECT_REL_PATH
from son_editor.app.database import db_session, scan_project_dir, sync_project_descriptor
from son_editor.app.exceptions import NotFound, InvalidArgument, NameConflict
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace

# Github domains to check if github is used
GITHUB_DOMAINS = ['github.com', 'www.github.com']

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
    args = ['git']
    args.extend(git_args)
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

    # Prioritize err message
    if err:
        result_dict.update({'message': err})
    elif out:
        result_dict.update({'message': out})
    if exitcode:
        result_dict.update({'exitcode': exitcode})
    return result_dict


def get_project(ws_id, pj_id: int) -> Project:
    project = db_session().query(Project).join(Workspace). \
        filter(Workspace.id == ws_id). \
        filter(Project.id == pj_id).first()
    if not project:
        raise NotFound("Could not find project with id {}".format(pj_id))
    return project


def get_workspace(ws_id: int) -> Workspace:
    workspace = db_session().query(Workspace).filter(Workspace.id == ws_id).first()
    if not workspace:
        raise NotFound("Could not find workspace with id {}".format(ws_id))
    return workspace


def commit_and_push(ws_id: int, project_id: int, commit_message: str):
    """
    Commits and then pushes changes.
    :param ws_id:
    :param project_id:
    :param commit_message:
    :return:
    """
    project = get_project(ws_id, project_id)

    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)
    # Stage all modified, added, removed files
    out, err, exitcode = git_command(['add', '-A'], cwd=project_full_path)
    if exitcode is not 0:
        return create_info_dict(out, err=err, exitcode=exitcode)

    # Commit with message
    out, err, exitcode = git_command(['commit', "-m '{}'".format(commit_message)], cwd=project_full_path)
    if exitcode is not 0:
        git_command(['reset', 'HEAD~1'], cwd=project_full_path)
        return create_info_dict(out, err=err, exitcode=exitcode)

    # Push all changes to the repo url
    url_decode = parse.urlparse(project.repo_url)
    out, err, exitcode = git_command(['push', _get_repo_url(url_decode)], cwd=project_full_path)
    if exitcode is not 0:
        git_command(['reset', 'HEAD~1'], cwd=project_full_path)
        return create_info_dict(out, err=err, exitcode=exitcode)

    # Success on commit
    return create_info_dict(out)


def pull(ws_id: int, project_id: int):
    """
    Pulls data from the given project_id.
    :param user_data: Session data to get access token for GitHub
    :param ws_id:
    :param project_id:
    :return:
    """
    project = get_project(ws_id, project_id)

    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)

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
    return create_info_dict(out=out)


def clone(ws_id: int, url: str, name: str = None):
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
        github_project_name = name
        if github_project_name is None:
            github_project_name = os.path.split(url_decode.path)[-1]

        pj = db_session().query(Project).filter(Workspace.id == workspace.id).filter(
            Project.name == github_project_name).first()

        # Error when the project name in given workspace already exists
        if pj is not None:
            raise NameConflict('A project with name {} already exists'.format(github_project_name))

        project_target_path = os.path.join(workspace.path, PROJECT_REL_PATH, github_project_name)

        logger.info('Cloning from github repo...')

        # If url in GitHub domain, access by token
        url_with_token = _get_repo_url(url_decode)
        out, err, exitcode = git_command(['clone', url_with_token, project_target_path])

        if exitcode is 0:
            # Create project and scan it.
            dbsession = db_session()
            try:
                pj = Project(github_project_name, github_project_name, workspace)
                pj.repo_url = url
                sync_project_descriptor(pj)
                dbsession.add(pj)
                scan_project_dir(project_target_path, pj)
                dbsession.commit()
                result = create_info_dict(out=out)
                result["id"] = pj.id
                return result
            except:
                dbsession.rollback()
                shutil.rmtree(project_target_path)
                raise Exception("Scan project failed")
        else:
            return create_info_dict(err=err, exitcode=exitcode)

    raise NotImplemented("Cloning from other is not implemented yet. Only github supported for now.")


def _get_repo_url(url_decode):
    return 'https://{}@github.com/{}'.format(session['access_token'], url_decode.path)
