from son.editor.app.util import CONFIG
import tempfile
print("Setting up config for temporary db")
handle, CONFIG['database']['location'] = tempfile.mkstemp()

from son.editor.app.database import init_db
init_db()
