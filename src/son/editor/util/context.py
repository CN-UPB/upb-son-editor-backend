from son.editor.app import __main__
from son.editor.app.database import reset_db


# Initializes a test-case context
def init_test_context():
    __main__.app.config['TESTING'] = True
    return __main__.app.test_client()
    reset_db()
