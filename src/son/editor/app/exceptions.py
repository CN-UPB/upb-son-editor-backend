class NameConflict(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class NotFound(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg