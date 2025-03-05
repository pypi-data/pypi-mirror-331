from .DatabaseManager import DatabaseManager
from onbbu.settings import installed_apps
from onbbu.database import DatabaseManager

database: DatabaseManager = DatabaseManager(INSTALLED_APPS=installed_apps)

__all__ = [
    "DatabaseManager",
    "database"
]
