import logging

logger = logging.getLogger("son-editor.exceptions")


class NameConflict(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class NotFound(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class ExtNotReachable(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class PackException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg
