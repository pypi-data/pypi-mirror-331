import os
import sys
from onbbu.database import DatabaseManager
from onbbu.logger.main import Logger
from onbbu.network.ServerHttp import ServerHttp
from onbbu.settings.ConfigLoader import ConfigLoader

BASE_DIR: str = os.getcwd()

sys.path.append(BASE_DIR)

environment: str = os.getenv("ENVIRONMENT", "development")

logger: Logger = Logger(log_file=None, server_url=None)

server: ServerHttp = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/main.py",
    attribute_name="server",
    default=None,
)

installed_apps = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/settings.py",
    attribute_name="INSTALLED_APPS",
    default=[],
)

database: DatabaseManager = DatabaseManager(INSTALLED_APPS=installed_apps)
