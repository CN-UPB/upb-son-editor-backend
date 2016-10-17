import logging
import tempfile

from son_editor.util.requestutil import CONFIG

logging.info("Setting up config for temporary db")

# Set the temp db location
handle, CONFIG['database']['location'] = tempfile.mkstemp()

# import after database location has been set to a temp directory
from son_editor.app.database import init_db

# Testing flag to circumvent login
CONFIG['testing'] = True
# set workspacelocation to tempfile to avoid spamming the workspace dir
CONFIG["workspaces-location"] = tempfile.mkdtemp() + '/'

# Initialize db with the temp location
init_db()
