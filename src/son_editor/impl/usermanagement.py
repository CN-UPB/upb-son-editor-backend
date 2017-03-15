'''
Created on 05.08.2016

@author: Jonas
'''
import json
import shlex

import flask
import requests

from son_editor.app.database import db_session
from son_editor.app.exceptions import UnauthorizedException
from son_editor.models.user import User
from son_editor.util.requestutil import get_config


def get_user(login: str):
    """
    Gets the user from the Database if it exists or
    creates a new user in the Database using the
    login data from the session. If the database does
    not yet have the full user Data it is queried
    from Github using the access Token

    :return: The database user model
    """

    session = db_session()
    user_name = shlex.quote(login)

    user = session.query(User).filter(User.name == user_name).first()
    # for now: if user does not exist we will create a user
    # (that has no access to anything he has not created)
    if user is None:
        user = User(name=user_name)
        session.add(user)
    if user.email is None:

        if 'users' in get_config()['authentication']:
            # check if user is in list of authorized users
            if user_name not in get_config()['authentication']['users']:
                raise UnauthorizedException(
                    user_name + " was not found in the list of valid users,"
                                "Please ask the admin of this server to add "
                                "you to the list of valid users")

        headers = {"Accept": "application/json",
                   "Authorization": "token " + flask.session['access_token']}
        result = requests.get('https://api.github.com/user/emails', headers=headers)
        user_emails = json.loads(result.text)

        for email in user_emails:
            if email['primary']:
                user.email = shlex.quote(email['email'])
                break

    session.commit()
    return user
