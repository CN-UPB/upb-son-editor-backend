from son.editor.app import __main__
from son.editor.app.database import reset_db
from son.editor.app.util import CONFIG


# Initializes a test-case context
def init_test_context():
    CONFIG['testing'] = True
    return __main__.app.test_client()
    reset_db()
