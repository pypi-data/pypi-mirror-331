from contextlib import asynccontextmanager
from dataclasses import dataclass
import multiprocessing

from starlette.applications import Starlette

from onbbu.settings.ConfigLoader import ConfigLoader
from onbbu.database import DatabaseManager
from onbbu.settings.main import BASE_DIR, environment


class ServerHttp:
    def __init__(self, port=8000):
        self.host = "0.0.0.0"
        self.port = port
        self.environment = environment
        self.reload = self.environment == "development"
        self.workers = 1 if self.reload else max(2, multiprocessing.cpu_count() - 1)

        self.installed_apps = self._load_installed_apps()

        self.database = DatabaseManager(INSTALLED_APPS=self.installed_apps)

        self.server = Starlette(debug=True, routes=[], lifespan=self._lifespan)

        self.config = ConfigInit(http=self.server)

    def _load_installed_apps(self):
        """Load `INSTALLED_APPS` from `internal/settings.py` if it exists"""

        installed_apps = ConfigLoader(BASE_DIR).load_python_config(
            relative_path="internal/settings.py",
            attribute_name="INSTALLED_APPS",
            default=[],
        )

        return installed_apps

    @asynccontextmanager
    async def _lifespan(self, app: Starlette):
        """Gestor de eventos de vida para FastAPI"""
        await self.database.init_db()
        yield
        await self.database.close_db()


def create_app(port=8000) -> ServerHttp:
    """Crea y retorna una instancia del servidor."""
    return ServerHttp(port=port)


@dataclass(frozen=True, slots=True)
class ConfigInit:
    http: ServerHttp
