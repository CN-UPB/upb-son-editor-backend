'''
Created on 05.08.2016

@author: Jonas
'''
import json
import shlex

import flask
import requests

from son.editor.app.database import db_session
from son.editor.models.user import User


def get_user(user_data):
    session = db_session()
    userName = shlex.quote(user_data['login'])

    user = session.query(User).filter(User.name == userName).first()
    # for now: if user does not exist we will create a user
    # (that has no access to anything he has not created)
    if user is None:
        headers = {"Accept": "application/json",
                   "Authorization": "token " + flask.session['access_token']}
        result = requests.get('https://api.github.com/user/emails', headers=headers)
        user_emails = json.loads(result.text)

        user = User(name=userName)

        for email in user_emails:
            if email['primary']:
                user.email = shlex.quote(email['email'])
                break

        session.add(user)
        session.commit()
    return user
