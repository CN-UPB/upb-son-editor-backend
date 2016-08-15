import tempfile
import logging

from son.editor.app.util import CONFIG

print("Setting up config for temporary db")

# Set the temp db location
handle, CONFIG['database']['location'] = tempfile.mkstemp()

# import after database location has been set to a temp directory
from son.editor.app.database import init_db

# Testing flag to circumvent login
CONFIG['testing'] = True

# Initialize db with the temp location
init_db()
