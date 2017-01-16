'''
Created on 22.07.2016

@author: Jonas
'''
from enum import Enum

# URL REST constants
"""The workspace url constant"""
WORKSPACES = "workspaces"
"""The project url constant"""
PROJECTS = "projects"
"""The platform url constant"""
PLATFORMS = "platforms"
"""the platform url constant"""
CATALOGUES = "catalogues"
"The network service url constant"
SERVICES = "services"
"""The virtual network function url constant"""
VNFS = "functions"
""" The network services and funtions url constant"""
NSFS = "nsfs"
""" The git api url constant"""
GIT = "git"

# PATH constants
"""The project path relative to the workspace"""
PROJECT_REL_PATH = "projects"

# Files that are required to be in terms of file structure, a valid son-project
REQUIRED_SON_PROJECT_FILES = ['project.yml']


class Github():
    """
    Holds GitHub API relevant strings.
    """
    DOMAINS = ['github.com', 'www.github.com']

    API_URL = 'https://api.github.com'
    API_CREATE_REPO_REL = '/user/repos'

    """
    1. Argument is owner of the repos to delete
    2. Argument is the name of the remote repository
    """
    API_DELETE_REPO = '/repos/{}/{}'
    """
        1. Argument is Username
    """
    API_LIST_REPOS = '/users/{}/repos'


class Category(Enum):
    project = 1
    catalogue = 2
    platform = 3


def get_parent(request):
    """Helper method to extract the parent category
    for the services and functions api calls"""
    parent = str(request.url_rule).split(sep="/")[3]
    return {
        PROJECTS: Category.project,
        CATALOGUES: Category.catalogue,
        PLATFORMS: Category.platform
    }[parent]
