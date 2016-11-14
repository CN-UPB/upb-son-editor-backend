import json
import logging

import requests
from flask import request, redirect
from flask import session

from son_editor.util.requestutil import CONFIG

logger = logging.getLogger(__name__)


def get():
    """ Login the User with a referral code from the github oauth process"""
    session['session_code'] = request.args.get('code')
    if request_access_token() and load_user_data():
        logger.info("User " + session['user_data']['login'] + " logged in")
        if request.referrer is not None and 'github' not in request.referrer:
            origin = origin_from_referrer(request.referrer)
            return redirect(origin + CONFIG['frontend-redirect'])
        return redirect(CONFIG['frontend-host'] + CONFIG['frontend-redirect'])


def request_access_token():
    """ Request an access token from Github using the referral code"""
    # TODO add error handling
    data = {'client_id': CONFIG['authentication']['ClientID'],
            'client_secret': CONFIG['authentication']['ClientSecret'],
            'code': session['session_code']}
    headers = {"Accept": "application/json"}
    access_result = requests.post('https://github.com/login/oauth/access_token',
                                  json=data, headers=headers)
    session['access_token'] = json.loads(access_result.text)['access_token']
    return True


def load_user_data():
    """Load user data using the access token"""
    # TODO add error handling
    headers = {"Accept": "application/json",
               "Authorization": "token " + session['access_token']}
    user_data_result = requests.get('https://api.github.com/user', headers=headers)
    user_data = json.loads(user_data_result.text)
    session['user_data'] = user_data
    logger.info("user_data: %s" % user_data)
    return True


def get_user_info():
    """Returns current user information"""
    # Only allow logged in users to retrieve user information
    if session['access_token'] in session:
        return session['user_data']
    else:
        return "Unauthorized", 401


def logout():
    """Logs out the current user and removes all session related stuff
    :return: Redirect
    """
    # Remove all session related informations
    session.clear()
    return "logged out", 200


def origin_from_referrer(referrer):
    double_slash_index = referrer.find("//")
    return referrer[0:referrer.find("/", double_slash_index + 2)]
