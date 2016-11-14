from flask_restplus import Resource, Namespace

from son_editor.impl.userserviceimpl import *

namespace = Namespace("", description="User Service API")


@namespace.route("/user")
@namespace.response(200, "OK")
class Information(Resource):
    def get(self):
        """ Returns github information about the current user """
        return get_user_info()


@namespace.route("/logout")
@namespace.response(200, "OK")
class Logout(Resource):
    """ Logs out the current user """

    def get(self):
        return logout()


@namespace.route("/login", endpoint="login")
@namespace.response(200, "OK")
class Login(Resource):
    def get(self):
        """ Login the User with a referral code from the github oauth process"""
        return get()

    @staticmethod
    def request_access_token():
        """ Request an access token from Github using the referral code"""
        return request_access_token()

    @staticmethod
    def load_user_data():
        """Load user data using the access token"""
        # TODO add error handling
        return load_user_data()

    @staticmethod
    def origin_from_referrer(referrer):
        return origin_from_referrer()
