import logging

logger = logging.getLogger(__name__)


class StillReferenced(Exception):
    """
    Thrown whenever an action is taken towards an element that is still 
    referenced by another that would compromise the relationship like 
    deleting the referenced object
    """

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class NameConflict(Exception):
    """ Thrown whenever a name conflict arises for names that must be unique"""
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class InvalidArgument(Exception):
    """ Thrown whenever an argument is missing data or is supplying the wrong data"""
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


class NotFound(Exception):
    """ Thrown whenever a resource cannot be located, or the user has no access to it """
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class ExtNotReachable(Exception):
    """ Thrown whenever an external host cannot be contacted, be it because of a wrong url or network problems"""
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class PackException(Exception):
    """ Thrown whenever a service cannot be packaged by son-package, wraps the cli tools error message"""
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class UnauthorizedException(Exception):
    """ Thrown whenever an unauthorized access is detected, e.g. because the user has not yet logged in"""
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg
