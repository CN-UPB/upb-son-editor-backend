from son_editor.app import __main__
from son_editor.app.database import reset_db
from son_editor.util.requestutil import CONFIG, get_config
from os import path
import shutil

# URL
CATALOGUE_INSTANCE_URL = get_config()['test']['catalogue-instance']


def init_test_context():
    """
     Initializes a test-case context and cleans up workspace location beforehand
    :return:
    """
    CONFIG['testing'] = True
    # Delete existing workspaces
    shutil.rmtree(path.expanduser(CONFIG["workspaces-location"]), ignore_errors=True)
    reset_db()
    return __main__.app.test_client()
