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


"""Clones a repository given the url as json"""


def create(user_data, ws_id: int, url: str):
    dbsession = db_session()
    workspace = dbsession.query(Workspace).filter(Workspace.id == ws_id).first()
    url_decode = parse.urlparse(url)

    if is_github(url_decode.netloc):
        # If url in github domain, access by token
        logger.info('Cloning from github repo...')
        url_with_token = 'https://{}@github.com/{}'.format(session['access_token'], url_decode.path)
        gitproc = Popen(['git', 'clone', url,
                         workspace.path + "/" + PROJECT_REL_PATH + "/{}".format(os.path.split(url_decode.path)[-1])],
                        stdout=PIPE, stderr=PIPE)

        out, err = gitproc.communicate()
        exitcode = gitproc.returncode
        if exitcode is not 0:
            raise NameConflict(err.decode())

    else:
        logger.info('Cloning from another repo...')
        # gitproc = check_call(['git', 'clone', url])
    return True
