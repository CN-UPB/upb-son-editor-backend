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
from son_editor.impl import usermanagement
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
    :return: the relative GitHub api url
    """
    return Github.API_URL + Github.API_DELETE_REPO.format(owner, repo_name)


def is_github(netloc):
    """
    Checks if the given url is on github

    :param netloc: http url
    :return: True if on github, False else
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
    result_dict = {}

    # Prioritize err message
    if err:
        result_dict.update({'message': err})
    elif out:
        result_dict.update({'message': out})

    if exitcode:
        # Frontend parses '\n' to <br>
        output = (out + "\n" if out else '') + (err if err else '')

    return result_dict


def get_project(ws_id, pj_id: int, session=db_session()) -> Project:
    """
    Returns a project and raises 404, when project not found.

    :param ws_id: Workspace id
    :param pj_id: Project id
    :param session: db session
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

    :param project_path: the path of the cloned project
    """
    missing_files = []

    files = [f for f in os.listdir(project_path)]
    logger.warn('Files in {}: '.format(project_path))
    for f in files:
        logger.warn('{}'.format(f))

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

    # Delete project, if there are missing files.
    shutil.rmtree(project_path)

    raise InvalidArgument(result)


def get_workspace(ws_id: int) -> Workspace:
    """
    Returns the workspace model of the given workspace

    :param ws_id: The workspace ID
    :return: The corresponding workspace model
    """
    workspace = db_session().query(Workspace).filter(Workspace.id == ws_id).first()
    if not workspace:
        raise NotFound("Could not find workspace with id {}".format(ws_id))
    return workspace


def init(ws_id: int, project_id: int):
    """
    Initializes a git repository in the given project

    :param ws_id: The workpace ID
    :param project_id: The project ID to initialize
    :return: a dictionary containing the result of the operation
    """
    project = get_project(ws_id, project_id)

    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)
    out, err, exitcode = git_command(['init'], cwd=project_full_path)
    # Additionally set repository user information
    if exitcode is 0:
        setup_git_user_email(project_full_path)
    return create_info_dict(out, err=err, exitcode=exitcode)


def setup_git_user_email(project_full_path: str):
    """
    Setting up the git user in the local git config to be able to make commits and push
    
    :param project_full_path: The absolute project path
    """
    user = usermanagement.get_user(session['user_data']['login'])
    git_command(['config', 'user.name', user.name], cwd=project_full_path)
    git_command(['config', 'user.email', user.email], cwd=project_full_path)
    git_command(['config', 'push.default', 'simple'], cwd=project_full_path)


def commit_and_push(ws_id: int, project_id: int, commit_message: str):
    """
    Commits and then pushes changes.

    :param ws_id: The workspace ID
    :param project_id: The project ID
    :param commit_message: The commit message
    :return: a dictionary containing the result of the operation
    """
    project = get_project(ws_id, project_id)

    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)
    logger.warn("Commit and Push files")
    files = [f for f in os.listdir(project_full_path)]
    logger.warn('Files in {}: '.format(project_full_path))
    for f in files:
        logger.warn('{}'.format(f))

    # Stage all modified, added, removed files
    out, err, exitcode = git_command(['add', '-A'], cwd=project_full_path)
    if exitcode is not 0:
        return create_info_dict(out, err=err, exitcode=exitcode)
    else:
        logger.warn("Add succeeded: {}".format(out))

    # Commit with message
    out, err, exitcode = git_command(['commit', "-m '{}'".format(commit_message)], cwd=project_full_path)
    if exitcode is not 0:
        if 'up-to-date' not in out:
            git_command(['reset', 'HEAD~1'], cwd=project_full_path)
            return create_info_dict(out, err=err, exitcode=exitcode)
        else:
            logger.warn("Nothing to commit. Trying to push anyways".format(out))
    else:
        logger.warn("Commit succeeded: {}".format(out))

    # Push all changes to the repo url
    sout, serr, sexitcode = git_command(['status', '-u'], cwd=project_full_path)
    url_decode = parse.urlparse(project.repo_url)
    logger.warn("Executed status".format(out))
    git_command(['remote', 'rm', 'origin', _get_repo_url(url_decode)], cwd=project_full_path)
    git_command(['remote', 'add', 'origin', _get_repo_url(url_decode)], cwd=project_full_path)
    git_command(['push', '--set-upstream', 'origin', 'master'], cwd=project_full_path)
    git_command(['push', '-u'], cwd=project_full_path)
    # time.sleep(30)
    if exitcode is not 0:
        git_command(['reset', 'HEAD~1'], cwd=project_full_path)
        return create_info_dict(out, err=err, exitcode=exitcode)
    else:
        logger.warn("Push succeeded: {}".format(out))
    logger.warn("Push out: {}\n err: {} \n exitcode: {}\n repo url: {}".format(out, err, exitcode,
                                                                               _get_repo_url(url_decode)))
    logger.warn("Status: out: {}\n err: {} \n exitcode: {}\n".format(sout, serr, sexitcode))

    # Success on commit
    return create_info_dict(out)


def create_commit_and_push(ws_id: int, project_id: int, remote_repo_name: str):
    """
    Creates a remote GitHub repository named remote_repo_name and pushes given git project into it.

    :param ws_id: Workspace ID
    :param project_id: Project ID to create and push it
    :param remote_repo_name: Remote repository name
    :return: a dictionary containing the result of the operation
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
        git_url = data['svn_url']
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


def delete(ws_id: int, project_id: int, remote_repo_name: str, organization_name: str = None):
    """
    Deletes given project on remote repository

    :param project_id:
    :param ws_id: Workspace of the project
    :param remote_repo_name: Remote repository name
    :param organization_name: Optional parameter to specify the organization / login
    :return: a dictionary containing the result of the operation
    """
    if organization_name is None:
        owner = session['user_data']['login']
    else:
        owner = organization_name
    sql_session = db_session()
    project = get_project(ws_id, project_id, sql_session)
    url_decode = parse.urlparse(project.repo_url)
    if _repo_name_from_url(url_decode) == remote_repo_name:
        result = _do_delete(owner, remote_repo_name)
        if result.status_code == 204:
            project.repo_url = None
            sql_session.commit()
            return create_info_dict("Successfully deleted")
        else:
            sql_session.rollback()
            return create_info_dict(result.text, exitcode=1)
    raise InvalidArgument("The given repo name does not correspond to the remote repository name")


def _do_delete(owner, remote_repo_name):
    """
    Executes the delete api call at the given remote repo
    
    :param owner: The  github user name of the repository owner
    :param remote_repo_name: The remote repository name
    :return: The APIs answer
    """
    return requests.delete(build_github_delete(owner, remote_repo_name), headers=create_oauth_header())


def diff(ws_id: int, pj_id: int):
    """
    Shows the local changes of the given project.

    :param ws_id: Workspace of the project.
    :param pj_id: Given project to show from.
    :return: a dictionary containing the result of the operation
    """
    project = get_project(ws_id, pj_id)
    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)

    out, err, exitcode = git_command(['diff'], project_full_path)
    if exitcode is 0:
        return create_info_dict(out)
    else:
        return create_info_dict(out, err, exitcode)


def status(ws_id: int, pj_id: int):
    """
    Shows the git status of the repository

    :param ws_id: The workspace ID
    :param pj_id: The project ID
    :return: a dictionary containing the result of the operation
    """
    project = get_project(ws_id, pj_id)
    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)

    # fetch remote changes
    out, err, exitcode = git_command(['remote', 'update'], project_full_path)
    if exitcode is 0:
        # get the status
        out, err, exitcode = git_command(['status', '-uno', '-u'], project_full_path)
        if exitcode is 0:
            return create_info_dict(out)
    return create_info_dict(out, err, exitcode)


def pull(ws_id: int, project_id: int):
    """
    Pulls data from the given project_id.
    :param ws_id: Workspace of the project
    :param project_id: Project to pull.
    :return: a dictionary containing the result of the operation
    """
    dbsession = db_session()
    project = get_project(ws_id, project_id, session=dbsession)

    project_full_path = os.path.join(project.workspace.path, PROJECT_REL_PATH, project.rel_path)

    # Error handling
    if not os.path.isdir(project_full_path):
        raise Exception("Could not find project directory {}".format(project_full_path))

    if not project.repo_url:
        raise InvalidArgument("Project with id {} is missing the repo attribute".format(project_id))

    # Pull in project directory
    # If url in GitHub domain, access by token
    out, err, exitcode = git_command(['pull', project.repo_url], cwd=project_full_path)

    # Return error if pull failed.
    if exitcode is not 0:
        return create_info_dict(err=err, exitcode=exitcode)

    # Rescan project
    try:
        sync_project_descriptor(project)
        dbsession.add(project)
        scan_project_dir(project_full_path, project)
        dbsession.commit()
    except:
        dbsession.rollback()
        raise Exception("Could not scan the project after pull.")

    return create_info_dict(out=out)


def list():
    """
    Lists the available remote repositories.

    :param ws_id: The workspace ID
    :return: https://developer.github.com/v3/repos/#response
    """
    result = requests.get(Github.API_URL + Github.API_LIST_REPOS.format(session['user_data']['login']),
                          headers=create_oauth_header())
    return json.loads(result.text)


def _repo_name_from_url(url_decode: str):
    """
    Extracts the repository name from its URL
    :param url_decode: 
    :return: 
    """
    github_project_name = os.path.split(url_decode.path)[-1]
    return github_project_name.replace('.git', '')


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
            github_project_name = _repo_name_from_url(url_decode)
        dbsession = db_session()
        pj = dbsession.query(Project).join(Workspace)\
            .filter(Workspace.id == workspace.id).filter(
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
