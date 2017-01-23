import json
import logging
import os
import shutil
import time
from subprocess import Popen, PIPE
from urllib import parse

import requests
from flask import session

from son_editor.app.database import db_session, scan_project_dir, sync_project_descriptor
from son_editor.app.exceptions import NotFound, InvalidArgument, NameConflict
from son_editor.models.project import Project
from son_editor.models.workspace import Workspace
from son_editor.util.constants import PROJECT_REL_PATH, Github, REQUIRED_SON_PROJECT_FILES

logger = logging.getLogger(__name__)


def create_oauth_header() -> dict:
    """
    Creates oauth header by providing the access token in the header.
    :return: Header as dict
    """
    return {'Authorization': 'token {}'.format(session['access_token'])}


def build_github_delete(owner: str, repo_name: str) -> str:
    """
    Builds relative github api url to delete a repository
    :param owner: Owner of the github repository
    :param repo_name: Repository name
    :return:
    """
    return Github.API_URL + Github.API_DELETE_REPO.format(owner, repo_name)


def is_github(netloc):
    """
    Checks if the given url is on github
    :param netloc: http url
    :return: True
    """

    if netloc.lower() in Github.DOMAINS:
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


def get_project(ws_id, pj_id: int, session=db_session()) -> Project:
    """
    Returns a project and raises 404, when project not found.
    :param ws_id: Workspace id
    :param pj_id: Project id
    :param db session
    :return: Project model
    """
    project = session.query(Project).join(Workspace) \
        .filter(Workspace.id == ws_id) \
        .filter(Project.id == pj_id).first()
    if not project:
        raise NotFound("Could not find project with id {}".format(pj_id))
    return project


def check_son_validity(project_path: str):
    """
    Checks if the given project path is a valid son project, otherwise it raises an exception. Valid means, it has
    a consistent son file structure, so no semantics will be tested.
    :param project_path:
    :return:
    """
    missing_files = []
    for file in REQUIRED_SON_PROJECT_FILES:
        if not os.path.isfile(os.path.join(project_path, file)):
            missing_files.append(file)

    missing_files_count = len(missing_files)
    # If project seems to be valid.
    if missing_files_count is 0:
        return
    elif missing_files_count is 1:
        result = "The project has no '{}' file".format(file)
    else:
        result = "The project has the following missing files: '{}'".format(",".join(missing_files_count))
    raise InvalidArgument(result)


def get_workspace(ws_id: int) -> Workspace:
    """
    Returns the workspace model of the given workspace
    :param ws_id:
    :return:
    """
    workspace = db_session().query(Workspace).filter(Workspace.id == ws_id).first()
    if not workspace:
        raise NotFound("Could not find workspace with id {}".format(ws_id))
    return workspace


def init(ws_id: int, project_id: int):
    """
    Initializes a git repository in the given project
    :param ws_id:
    :param project_id:
    :return:
    """
    project = get_project(ws_id, project_id)

    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)
    out, err, exitcode = git_command(['init'], cwd=project_full_path)
    # Additionally set repository user information
    if exitcode is 0:
        setup_git_user_email(project_full_path)
    return create_info_dict(out, err=err, exitcode=exitcode)


def setup_git_user_email(project_full_path: str):
    git_command(['config', 'user.name', session['user_data']['login']], cwd=project_full_path)
    git_command(['config', 'user.email', session['user_data']['email']], cwd=project_full_path)


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


def create_commit_and_push(ws_id: int, project_id: int, remote_repo_name: str):
    """
    Creates a remote GitHub repository named remote_repo_name and pushes given git project into it.

    :param ws_id: Workspace ID
    :param project_id: Project ID to create and push it
    :param remote_repo_name: Remote repository name
    :return:
    """
    database_session = db_session()
    try:
        project = get_project(ws_id, project_id, database_session)

        # curl -H "Authorization: token [TOKEN]" -X POST https://api.github.com/user/repos --data '{"name":"repo_name"}'

        repo_data = {'name': remote_repo_name}

        request = requests.post(Github.API_URL + Github.API_CREATE_REPO_REL, json=repo_data,
                                headers=create_oauth_header())

        # Handle exceptions
        if request.status_code != 201:
            # Repository already exists
            if request.status_code == 422:
                raise NameConflict("Repository with name {} already exist on GitHub".format(remote_repo_name))
            raise Exception("Unhandled status_code: {}\n{}".format(request.status_code, request.text))

        # Get git url and commit to db
        data = json.loads(request.text)
        git_url = data['git_url']
        project.repo_url = git_url
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise

    # Try to push project
    try:
        # Give github some time to see created repo
        # (dirty hack)
        time.sleep(0.5)

        return commit_and_push(ws_id, project_id, "Initial commit")
    except Exception:
        # Delete newly created repository if commit and push failed.
        result = requests.delete(build_github_delete(session['user_data']['login'], remote_repo_name),
                                 headers=create_oauth_header())
        # Reraise
        raise


def delete(ws_id: int, remote_repo_name: str, organization_name: str = None):
    """
    Deletes given project on remote repository
    :param ws_id: Workspace of the project
    :param remote_repo_name: Remote repository name
    :param organization_name: Optional parameter to specify the organization / login
    :return:
    """
    if organization_name is None:
        owner = session['user_data']['login']
    else:
        owner = organization_name

    result = requests.delete(build_github_delete(owner, remote_repo_name), headers=create_oauth_header())
    if result.status_code == 204:
        return create_info_dict("Successful deleted")
    else:
        return create_info_dict(result.text, exitcode=1)


def diff(ws_id: int, pj_id: int):
    """
    Shows the local changes of the given project.
    :param ws_id: Workspace of the project.
    :param pj_id: Given project to show from.
    :return:
    """
    project = get_project(ws_id, pj_id)
    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)

    out, err, exitcode = git_command(['diff'], project_full_path)
    if exitcode is 0:
        return create_info_dict(out)
    else:
        return create_info_dict(out, err, exitcode)


def pull(ws_id: int, project_id: int):
    """
    Pulls data from the given project_id.
    :param user_data: Session data to get access token for GitHub
    :param ws_id: Workspace of the project
    :param project_id: Project to pull.
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


def list(ws_id: int):
    """
    Lists the available remote repositories.
    :param ws_id:
    :return: https://developer.github.com/v3/repos/#response
    """
    result = requests.get(Github.API_URL + Github.API_LIST_REPOS.format(session['user_data']['login']),
                          headers=create_oauth_header())
    return json.loads(result.text)


def clone(ws_id: int, url: str, name: str = None):
    """
    Clones a repository by url into given workspace
    :param name: Optional name of the local repository name, otherwise the remote name is taken
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
        dbsession = db_session()
        pj = dbsession.query(Project).filter(Workspace.id == workspace.id).filter(
            Project.name == github_project_name).first()
        dbsession.commit()
        # Error when the project name in given workspace already exists
        if pj is not None:
            raise NameConflict('A project with name {} already exists'.format(github_project_name))

        project_target_path = os.path.join(workspace.path, PROJECT_REL_PATH, github_project_name)

        logger.info('Cloning from github repo...')

        # If url in GitHub domain, access by token
        url_with_token = _get_repo_url(url_decode)
        out, err, exitcode = git_command(['clone', url_with_token, project_target_path])

        if exitcode is 0:
            setup_git_user_email(project_target_path)
            # Check if the project is a valid son project
            check_son_validity(project_target_path)
            # Create project and scan it.
            dbsession = db_session()
            try:
                pj = Project(github_project_name, github_project_name, workspace)
                pj.repo_url = url
                sync_project_descriptor(pj)
                dbsession.add(pj)
                scan_project_dir(project_target_path, pj)
                dbsession.commit()
                # Check if the project is valid
                result = create_info_dict(out=out)
                result["id"] = pj.id
                return result
            except:
                dbsession.rollback()
                shutil.rmtree(project_target_path)
                raise Exception("Scan project failed")
        else:
            return create_info_dict(err=err, exitcode=exitcode)

    raise NotImplemented("Cloning from other is not implemented yet. Only github is supported for now.")


def _get_repo_url(url_decode):
    return 'https://{}@github.com{}'.format(session['access_token'], url_decode.path)
