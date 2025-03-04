import os
import sys
from onbbu.logger.main import Logger


BASE_DIR: str = os.getcwd()

sys.path.append(BASE_DIR)

environment: str = os.getenv("ENVIRONMENT", "development")

logger: Logger = Logger(log_file=None, server_url=None)
