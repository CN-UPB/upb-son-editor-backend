import contextlib
import logging
import os
from pathlib import Path

import shutil
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from son_editor.util.descriptorutil import load_ns_vnf_from_disk, load_workspace_descriptor, get_file_path, \
    get_file_name, \
    sync_project_descriptor
from son_editor.util.requestutil import get_config

# DB URI
logger = logging.getLogger(__name__)
DATABASE_SQLITE_URI = "sqlite:///%s" % get_config()['database']['location']
logger.info("DBSQLITE_URI: " + DATABASE_SQLITE_URI)

engine = create_engine(DATABASE_SQLITE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """
    Import model modules
    
    Import all modules here that might define models so that
        they will be registered properly on the metadata.  Otherwise
        you will have to import them first before calling init_db()
    """
    import son_editor.models.project
    import son_editor.models.user
    import son_editor.models.workspace
    import son_editor.models.descriptor
    import son_editor.models.repository
    import son_editor.models.private_descriptor
    Base.metadata.create_all(bind=engine)


def reset_db():
    """
    Resets the database  
    
    only used in tests
    """
    meta = Base.metadata

    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()


def scan_workspaces_dir():
    """
    Scan workpaces directory
    
    Scans the workpaces directory for any users.
        Will visit every one to add new workspaces etc via _scan_user_dir
    """
    from son_editor.models.user import User
    wss_dir = os.path.normpath(os.path.expanduser(get_config()["workspaces-location"]))
    if os.path.exists(wss_dir):
        session = db_session()
        for user_name in os.listdir(wss_dir):
            if not Path(os.path.join(wss_dir, user_name)).is_dir():
                continue
            user = session.query(User).filter(User.name == user_name).first()
            if user is None:
                logger.info("Found user: {}!".format(user_name))
                user = User(user_name)
                session.add(user)
                session.commit()
            _scan_user_dir(wss_dir, user)


def _scan_user_dir(ws_dir, user):
    """
    Scan users directory
    
    Scans the users directory for any workspaces.
        Will visit every one to add new projects etc via _scan_workspace_dir
        
    :param ws_dir: the workspace dir to scan
    :param user: the current user from the database to attach the workpace to
    """
    from son_editor.models.workspace import Workspace
    session = db_session()
    for ws_name in os.listdir(os.path.join(ws_dir, user.name)):
        ws = session.query(Workspace). \
            filter(Workspace.name == ws_name). \
            filter(Workspace.owner == user).first()
        ws_path = os.path.join(ws_dir, user.name, ws_name)
        if not Path(os.path.join(ws_path)).is_dir():
            continue
        if ws is None:
            logger.info("Found workspace at {}!".format(ws_path))
            ws = Workspace(ws_name, ws_path, user)
            load_workspace_descriptor(ws)
            session.add(ws)
            session.commit()
        _scan_workspace_dir(ws_path, ws)


def _scan_workspace_dir(ws_path, ws):
    """
    Scan a workspace directory

    Scans the workspace directory for any projects.
        Will visit every one to add new functions and services via scan_project_dir
        
    :param ws_path: the workspaces path to scan
    :param ws: the current workspace from the database to attach the projects to
    """
    from son_editor.models.project import Project
    session = db_session()
    # Scan private catalogue in workspace
    _scan_private_catalogue(ws_path + "/catalogues", ws)

    for project_name in os.listdir(os.path.join(ws_path, "projects")):
        if not Path(os.path.join(ws_path, "projects", project_name)).is_dir():
            continue
        pj = session.query(Project). \
            filter(Project.name == project_name). \
            filter(Project.workspace == ws).first()
        if pj is None:
            logger.info("Found project in Workspace {}: {}".format(ws_path, project_name))
            pj = Project(project_name, project_name, ws)
            sync_project_descriptor(pj)
            session.add(pj)
            session.commit()
        scan_project_dir(os.path.join(ws_path, "projects", project_name), pj)


def scan_project_dir(project_path, pj):
    """
    Scan project dir
    
    Scans the project dir for any new functions and services 
        via _scan_for_functions and _scan_for_services 
    
    :param project_path: The path of the project to scan
    :param pj: The project from the database to attach the descriptors to
    :return: 
    """
    _scan_for_services(os.path.join(project_path, "sources", "nsd"), pj)
    _scan_for_functions(os.path.join(project_path, "sources", "vnf"), pj)


def _scan_private_catalogue(catalogue_dir, ws):
    """
    Scans the private Workspace catalogue for new service and function 
        descriptors and adds them to the database 
    :param catalogue_dir: The directory of the private catalogue in the workspace 
    :param ws: The database workspace
    """
    from son_editor.models.private_descriptor import PrivateFunction, PrivateService
    # Configure ns catalogue path
    ns_path = Path(catalogue_dir + "/ns_catalogue/")
    vnf_path = Path(catalogue_dir + "/vnf_catalogue/")

    _scan_catalogue(ns_path, PrivateService(), ws)
    _scan_catalogue(vnf_path, PrivateFunction(), ws)


def _scan_catalogue(cat_path, model, ws):
    """
    Scan a private catalogue dir
    
    Scans the given catalogue path for new descriptors 
    and writes it into the descriptor model
    
    :param cat_path: The catalogue path containing either nss or vnfs 
    :param model: The descriptor model
    :param ws: The workspace to attach the descriptors to
    """
    from pathlib import Path
    from son_editor.models.private_descriptor import PrivateDescriptor
    session = db_session()
    try:
        for vendor in cat_path.iterdir():
            if not vendor.is_dir():
                continue
            for name in vendor.iterdir():
                if not name.is_dir():
                    continue
                for version in name.iterdir():
                    path = Path(str(version) + "/descriptor.yml")
                    if path.exists() and path.is_file():
                        logger.info("Found private ns/vnf: {}".format(path))
                        model = load_ns_vnf_from_disk(str(path), model)
                        model.workspace = ws
                        if not session.query(PrivateDescriptor).filter(PrivateDescriptor.uid == model.uid).first():
                            session.add(model)
                            session.commit()
                        else:
                            session.rollback()
    except:
        session.rollback()


def _scan_for_services(services_dir, pj):
    """
    Scan project for services
    
    Scans the given directory for services and adds them to the project.
    
    :param services_dir: The services directory in the project
    :param pj: The project model from the database
    """
    from son_editor.models.descriptor import Service
    session = db_session()
    try:
        for service_file in os.listdir(services_dir):
            if service_file.endswith(".yml"):
                service = Service()
                file_path = os.path.join(services_dir, service_file)
                load_ns_vnf_from_disk(file_path, service)
                db_service = session.query(Service). \
                    filter(Service.project == pj). \
                    filter(Service.name == service.name). \
                    filter(Service.vendor == service.vendor). \
                    filter(Service.version == service.version). \
                    first()
                if not db_service:
                    logger.info("Found service in project {}: {}".format(pj.name, service.uid))
                    service.project = pj
                    session.add(service)
                    session.commit()
                else:
                    session.rollback()
                if get_file_path("nsd", service) != file_path:
                    shutil.move(file_path, get_file_path("nsd", service))  # rename to expected name format
            elif os.path.isdir(os.path.join(services_dir, service_file)):
                _scan_for_services(os.path.join(services_dir, service_file), pj)
    except:
        session.rollback()


def _scan_for_functions(function_dir, pj):
    """
    Scan project for functions
    
    Scans the given directory for functions and adds them to the project.
    
    :param function_dir: The functions directory in the project
    :param pj: The project model from the database
    """
    session = db_session()
    from son_editor.models.descriptor import Function
    try:
        for function_folder in os.listdir(function_dir):
            folder_path = os.path.join(function_dir, function_folder)
            if os.path.isdir(folder_path):
                yaml_files = [file for file in os.listdir(folder_path) if file.endswith(".yml")]
                if len(yaml_files) == 1:
                    function = Function()
                    file_path = os.path.join(folder_path, yaml_files[0])
                    load_ns_vnf_from_disk(file_path, function)
                    db_function = session.query(Function). \
                        filter(Function.project == pj). \
                        filter(Function.name == function.name). \
                        filter(Function.vendor == function.vendor). \
                        filter(Function.version == function.version). \
                        first()
                    if not db_function:
                        logger.info("Found function in project {}: {}".format(pj.name, function.uid))
                        function.project = pj
                        session.add(function)
                        session.commit()
                    else:
                        function = db_function
                    # rename folder if necessary
                    target_folder = os.path.normpath(
                        get_file_path("vnf", function).replace(get_file_name(function), ''))
                    if os.path.normpath(folder_path) != target_folder:
                        shutil.move(folder_path, target_folder)
                        file_path = file_path.replace(folder_path, target_folder)
                    # rename file if necessary
                    if not os.path.exists(get_file_path("vnf", function)):
                        shutil.move(file_path, get_file_path("vnf", function))
                else:
                    logger.info("Multiple or no yaml files in folder {}. Ignoring".format(folder_path))

    except:
        logger.exception("Could not load function descriptor:")
    finally:
        session.rollback()
