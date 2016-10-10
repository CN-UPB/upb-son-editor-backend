from son_editor.app import __main__
from son_editor.app.database import reset_db
from son_editor.util.requestutil import CONFIG

# URL
CATALOGUE_INSTANCE_URL = "http://fg-cn-sandman2.cs.upb.de:4012"


# Initializes a test-case context
def init_test_context():
    CONFIG['testing'] = True
    reset_db()
    return __main__.app.test_client()