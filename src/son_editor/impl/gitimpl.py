from subprocess import Popen, PIPE
from urllib import parse
from flask import session
from son_editor.app.database import db_session
from son_editor.models.workspace import Workspace
from son_editor.app.exceptions import NameConflict
import logging
import os

GITHUB_DOMAINS = ['github.com', 'www.github.com']
PROJECT_REL_PATH = "/projects"

logger = logging.getLogger(__name__)


def is_github(netloc):
    """ Checks if the given url is on github """
    netloc = netloc.lower()
    if netloc in GITHUB_DOMAINS:
        return True
    return False


def pull(user_data, ws_id: int, project_id: int):
    """
    Pulls data from the given project_id.
    :param user_data: Session data to get access token for GitHub
    :param ws_id:
    :param project_id:
    :return:
    """


def clone(user_data, ws_id: int, url: str):
    """
    Clones a repository by url into given workspace
    :param user_data: Session data to get access token for GitHub
    :param ws_id: Destination workspace to clone
    :param url: URL of the source repository
    :return: True if successful, otherwise NameConflict is thrown
    """
    workspace = db_session().query(Workspace).filter(Workspace.id == ws_id).first()
    url_decode = parse.urlparse(url)

    if is_github(url_decode.netloc):
        # If url in github domain, access by token
        logger.info('Cloning from github repo...')
        url_with_token = 'https://{}@github.com/{}'.format(session['access_token'], url_decode.path)
        git_proc = Popen(['git', 'clone', url_with_token,
                          workspace.path + "/" + PROJECT_REL_PATH + "/{}".format(os.path.split(url_decode.path)[-1])],
                         stdout=PIPE, stderr=PIPE)

        out, err = git_proc.communicate()
        exitcode = git_proc.returncode
        if exitcode is not 0:
            raise NameConflict(err.decode())

    else:
        logger.info('Cloning from another repo...')
        raise NotImplemented("Cloning from other is not implemented yet.")
        # gitproc = check_call(['git', 'clone', url])
    return True
