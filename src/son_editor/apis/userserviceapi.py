from flask_restplus import Resource, Namespace

from son_editor.impl.userserviceimpl import *
from son_editor.util.requestutil import prepare_response

namespace = Namespace("", description="User Service API")


@namespace.route("/user")
@namespace.response(200, "OK")
class Information(Resource):
    """User information"""
    @staticmethod
    def get():
        """ Returns github information about the current user """
        return prepare_response(get_user_info())


@namespace.route("/logout")
@namespace.response(200, "OK")
class Logout(Resource):
    """ Logs out the current user """

    @staticmethod
    def get():
        return prepare_response(logout())


@namespace.route("/login", endpoint="login")
@namespace.response(200, "OK")
class Login(Resource):
    @staticmethod
    def get():
        """ Login the User with a referral code from the github oauth process"""
        return login()
