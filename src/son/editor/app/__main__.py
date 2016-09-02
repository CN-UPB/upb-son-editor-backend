'''
Created on 18.07.2016

@author: Jonas
'''
import logging
import urllib
from os import path
from sys import platform

from flask import Flask, session
from flask.globals import request
from flask_restplus import Api

from son.editor import catalogues
from son.editor import misc
from son.editor import platforms
from son.editor import projects
from son.editor import services
from son.editor import vnfs
from son.editor import workspaces
from son.editor.app.database import db_session, init_db
from son.editor.app.exceptions import NameConflict, NotFound
from son.editor.app.util import CONFIG, prepareResponse, prepareError

app = Flask(__name__)
# turn off help message for 404 errors, just return error handlers message
app.config["ERROR_404_HELP"] = False
app.config["RESTPLUS_MASK_SWAGGER"] = False
# load secret key from config
app.secret_key = CONFIG['session']['secretKey']
api = Api(app, description="Son Editor Backend API")
logger = logging.getLogger("son-editor.__main__")


@api.errorhandler(KeyError)
def handle_key_error(err):
    logger.exception(err.args[0])
    return prepareError({"message": "Key '{}' is required in request data!".format(err.args[0])}, 400)


@api.errorhandler(NotFound)
def handle_not_found(err):
    logger.warn(err.msg)
    return prepareError({"message": err.msg}, 404)


@api.errorhandler(NameConflict)
def handle_name_conflict(err):
    logger.warn(err.msg)
    return prepareError({"message": err.msg}, 409)


@api.errorhandler
def handle_general_exception(err):
    logger.exception(str(err))
    return prepareError({"message": str(err)}, getattr(err, 'code', 500))


# registering all the api resources here
workspaces.init(api)
projects.init(api)
services.init(api)
vnfs.init(api)
platforms.init(api)
catalogues.init(api)
misc.init(api)


# print(app.url_map)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.before_request
def checkLoggedIn():
    if request.method == 'OPTIONS':
        return prepareResponse()
    elif CONFIG['testing']:
        return
    elif 'access_token' not in session and request.endpoint not in ['login', 'static', 'shutdown']:
        args = {"scope": "user:email",
                "client_id": CONFIG['authentication']['ClientID']}
        session["requested_endpoint"] = request.endpoint
        return prepareResponse(
            {'authorizationUrl': 'https://github.com/login/oauth/authorize/?{}'.format(urllib.parse.urlencode(args))},
            401)


def setup():
    setup_logging()
    # Check check if database exists, otherwise create sqlite file
    dbFile = CONFIG['database']['location']
    if path.exists(dbFile):
        logger.info('Using database file "%s"' % dbFile)
    else:
        logger.info('Init database on "%s"' % dbFile)
        init_db()

    # Start the flask server
    logger.info("Launch flask server")


# Main entry point
def main(args=None):
    if platform == "darwin":
        app.run('0.0.0.0', debug=True)
    else:
        app.run('0.0.0.0')


def setup_logging():
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='editor-backend.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


setup()

if __name__ == "__main__":
    main()
