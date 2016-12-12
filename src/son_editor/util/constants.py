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

# PATH constants
"""The project path relative to the workspace"""
PROJECT_REL_PATH = "projects"


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
