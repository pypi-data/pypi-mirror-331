import os
import sys
from onbbu.ConfigLoader import ConfigLoader

BASE_DIR: str = os.getcwd()

sys.path.append(BASE_DIR)

environment: str = os.getenv("ENVIRONMENT", "development")

server = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/main.py",
    attribute_name="server",
    default=None,
)

installed_apps = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/settings.py",
    attribute_name="INSTALLED_APPS",
    default=[],
)

COMMANDS = {}