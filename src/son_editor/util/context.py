from son_editor.app import __main__
from son_editor.app.database import reset_db
from son_editor.util.requestutil import CONFIG


# Initializes a test-case context
def init_test_context():
    CONFIG['testing'] = True
    return __main__.app.test_client()
    reset_db()
