import json
import logging

import requests
from flask import request, redirect
from flask import session

from son_editor.app.exceptions import UnauthorizedException
from son_editor.util.requestutil import CONFIG

logger = logging.getLogger(__name__)


def login():
    """ Login the User with a referral code from the github oauth process"""
    session['session_code'] = request.args.get('code')
    if _request_access_token() and _load_user_data():
        logger.info("User " + session['user_data']['login'] + " logged in")
        if request.referrer is not None and 'github' not in request.referrer:
            origin = origin_from_referrer(request.referrer)
            return redirect(origin + CONFIG['frontend-redirect'])
        return redirect(CONFIG['frontend-host'] + CONFIG['frontend-redirect'])


def _request_access_token():
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


def _load_user_data():
    """Load user data using the access token"""
    # TODO add error handling
    if 'access_token' in session:
        headers = {"Accept": "application/json",
                   "Authorization": "token " + session['access_token']}
        user_data_result = requests.get('https://api.github.com/user', headers=headers)
        user_data = json.loads(user_data_result.text)
        session['user_data'] = user_data
        logger.debug("user_data: %s" % user_data)
        return True
    return False


def get_user_info()-> dict:
    """Returns current user information"""
    # Only allow logged in users to retrieve user information
    if 'access_token' in session and 'user_data' in session:
        return session['user_data']
    else:
        raise UnauthorizedException("Not logged in")


def logout():
    """Logs out the current user and removes all session related stuff
    :return: Redirect
    """
    # Remove all session related informations
    session.clear()
    return "logged out"


def origin_from_referrer(referrer):
    double_slash_index = referrer.find("//")
    return referrer[0:referrer.find("/", double_slash_index + 2)]
